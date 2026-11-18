#!/usr/bin/env python3
"""Coordinate Scripture import preflight and create a metadata-only staging hand-off.

This utility never writes D1, uploads R2 objects, or publishes Bible text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from scripture_import_preflight import load_json, run_preflight  # noqa: E402


class CoordinationError(RuntimeError):
    """Raised when a staging hand-off cannot be safely assembled."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def coordinate(
    *,
    manifest_path: Path,
    rights_path: Path,
    registry_path: Path,
    proposals_dir: Path | None,
    output_dir: Path,
    actor: str = "automated-preflight-coordinator",
) -> dict[str, Any]:
    manifest_path = manifest_path.resolve()
    rights_path = rights_path.resolve()
    registry_path = registry_path.resolve()
    if output_dir.exists():
        raise CoordinationError("Output directory must be new; existing run records are immutable.")
    manifest = load_json(manifest_path, "preflight manifest")
    rights = load_json(rights_path, "translation rights register")
    registry = load_json(registry_path, "USFM marker registry")
    if not isinstance(manifest, dict):
        raise CoordinationError("Preflight manifest must be a JSON object.")

    preflight = run_preflight(
        manifest, rights, registry,
        base_dir=manifest_path.parent,
        proposals_dir=proposals_dir.resolve() if proposals_dir else None,
    )
    archive = manifest.get("source_archive", {})
    archive_hash = archive.get("sha256") if isinstance(archive, dict) else None
    binding = {
        "edition_id": manifest.get("edition_id"),
        "source_id": manifest.get("source_id"),
        "archive_sha256": archive_hash,
        "manifest_sha256": sha256_file(manifest_path),
        "rights_register_sha256": sha256_file(rights_path),
        "marker_registry_sha256": sha256_file(registry_path),
        "preflight_report_sha256": canonical_hash(preflight),
    }
    run_id = "sir-" + canonical_hash(binding)[:24]
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    if preflight.get("ready_for_import") is True:
        handoff_status = "awaiting_manual_staging_authorization"
        next_action = "A named human operator must authorize a separate staging operation after verifying restricted object storage and approvals."
    else:
        handoff_status = "blocked"
        next_action = "Resolve every blocking preflight finding and create a new immutable coordination run."
    record = {
        "schema_version": 1,
        "record_type": "scripture_import_staging_handoff",
        "run_id": run_id,
        "created_at_utc": now,
        "created_by": actor,
        "state": "validated" if preflight.get("status") == "passed" else "validation_blocked",
        "handoff_status": handoff_status,
        "identity": {
            "edition_id": manifest.get("edition_id"),
            "source_id": manifest.get("source_id"),
            "territory": manifest.get("territory"),
            "source_archive_sha256": archive_hash,
            "manifest_sha256": binding["manifest_sha256"],
        },
        "input_fingerprints": binding,
        "preflight": {
            "status": preflight.get("status"),
            "ready_for_import": preflight.get("ready_for_import") is True,
            "summary": preflight.get("summary", {}),
            "findings": preflight.get("findings", []),
        },
        "controls": {
            "scripture_text_copied_to_handoff": False,
            "d1_written": False,
            "r2_written": False,
            "staging_authorized": False,
            "publication_authorized": False,
        },
        "next_action": next_action,
    }
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "preflight-report.json").write_text(
        json.dumps(preflight, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "staging-handoff.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "run_id": run_id,
        "handoff_status": handoff_status,
        "preflight_status": preflight.get("status"),
        "blocking_finding_count": preflight.get("summary", {}).get("blocking_finding_count", 1),
        "warning_count": preflight.get("summary", {}).get("warning_count", 0),
        "output_dir": str(output_dir),
        "d1_written": False,
        "r2_written": False,
        "publication_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--rights-register", type=Path, default=ROOT / "data/rights/translation-rights-register.json")
    parser.add_argument("--marker-registry", type=Path, default=ROOT / "data/usfm/marker-registry.json")
    parser.add_argument("--proposals-dir", type=Path, default=ROOT / "data/versification/proposals")
    parser.add_argument("--output-dir", type=Path, required=True, help="New private directory for metadata-only run records")
    parser.add_argument("--actor", default="automated-preflight-coordinator")
    args = parser.parse_args()
    try:
        result = coordinate(
            manifest_path=args.manifest,
            rights_path=args.rights_register,
            registry_path=args.marker_registry,
            proposals_dir=args.proposals_dir,
            output_dir=args.output_dir,
            actor=args.actor,
        )
    except (CoordinationError, OSError, ValueError) as exc:
        print(f"Staging coordination blocked: {type(exc).__name__}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result["handoff_status"] == "awaiting_manual_staging_authorization" else 2


if __name__ == "__main__":
    raise SystemExit(main())
