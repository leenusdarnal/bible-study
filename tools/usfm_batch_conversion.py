#!/usr/bin/env python3
"""Batch-convert the 66-book launch canon and emit a fail-closed preflight manifest.

All converted JSON contains Scripture wording. Keep the entire workspace private.
This tool does not upload objects, write D1, or publish translation text.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import usfm_to_structured_content as converter  # noqa: E402

CORE_66 = converter.CORE_66 if hasattr(converter, "CORE_66") else set("""
GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB
PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP
HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI
2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV
""".split())
SOURCES = {
    "engwebp": ("WEBP", "https://ebible.org/Scriptures/engwebp_usfm.zip"),
    "eng-kjv": ("KJV", "https://ebible.org/Scriptures/eng-kjv_usfm.zip"),
}
PARSER_VERSION = "0.4.10"
CONVERTER_META = {"name": "bible-study-usfm-structured-converter", "version": "0.1.0"}


class BatchError(RuntimeError):
    """Raised when source inventory or conversion cannot be trusted."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BatchError(f"Cannot read {path.name}: {type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise BatchError(f"{path.name} must contain a JSON object.")
    return value


def classify_member(book_ids: list[str]) -> tuple[str, str | None]:
    """Only pure Protestant-canon members enter the launch conversion."""
    ids = set(book_ids)
    if ids and ids.issubset(CORE_66):
        return "included", None
    if ids & CORE_66:
        return "excluded", "Mixed canon/non-canon member requires manual source separation."
    if ids:
        return "excluded", "Outside the initial 66-book Protestant canon."
    return "excluded", "Front matter or non-book USFM material; not Scripture-book content."


def _semantic_member_index(report: dict[str, Any], source_id: str) -> dict[str, dict[str, Any]]:
    if report.get("schema_version") != 2:
        raise BatchError("Semantic audit report must use schema_version 2.")
    index: dict[str, dict[str, Any]] = {}
    for row in report.get("files", []):
        if row.get("source_id") != source_id:
            continue
        name = row.get("member_name")
        if not isinstance(name, str) or name in index:
            raise BatchError("Semantic audit contains an invalid or duplicate member path.")
        index[name] = row
    return index


def run_batch(
    *, source_id: str, source_audit: dict[str, Any], semantic_audit: dict[str, Any],
    source_root: Path, registry_path: Path, output_root: Path, territory: str,
) -> dict[str, Any]:
    if source_id not in SOURCES:
        raise BatchError("source_id must be engwebp or eng-kjv.")
    edition_id, official_url = SOURCES[source_id]
    if source_audit.get("source_id") != source_id:
        raise BatchError("Source-audit report does not match the selected source.")
    archive_meta = source_audit.get("archive", {})
    if not isinstance(archive_meta, dict):
        raise BatchError("Source-audit archive metadata is missing.")
    inventory = source_audit.get("member_inventory")
    if not isinstance(inventory, list) or not inventory:
        raise BatchError("Complete source archive member inventory is required.")
    semantic_index = _semantic_member_index(semantic_audit, source_id)
    registry = converter.load_registry(registry_path)
    output_root.mkdir(parents=True, exist_ok=False)
    converted_dir = output_root / "converted"
    canonical_dir = output_root / "canonical-usx-local"
    converted_dir.mkdir()
    canonical_dir.mkdir()
    members: list[dict[str, Any]] = []
    included_books: set[str] = set()
    profile_counts: dict[str, int] = {}

    source_root = source_root.resolve()
    for record in inventory:
        if not isinstance(record, dict):
            raise BatchError("Source archive inventory contains a malformed member.")
        name = record.get("member_name")
        if not isinstance(name, str):
            raise BatchError("Source archive inventory member has no path.")
        rel = PurePosixPath(name)
        if rel.is_absolute() or any(part in {"", ".", ".."} for part in rel.parts):
            raise BatchError(f"Unsafe archive member path: {name}")
        source_path = (source_root / Path(*rel.parts)).resolve()
        if not source_path.is_relative_to(source_root) or not source_path.is_file():
            raise BatchError(f"Extracted source member is missing or escapes its root: {name}")
        raw = source_path.read_bytes()
        member_sha = digest(raw)
        if member_sha != record.get("sha256_uncompressed"):
            raise BatchError(f"Source checksum mismatch for {name}.")
        book_ids = record.get("book_ids", [])
        if not isinstance(book_ids, list) or any(not isinstance(x, str) for x in book_ids):
            raise BatchError(f"Invalid book IDs for {name}.")
        inclusion, exclusion_reason = classify_member(book_ids)
        semantic = semantic_index.get(name)
        if semantic is None:
            raise BatchError(f"Semantic audit omitted archive member: {name}")
        passing = [
            item for item in semantic.get("profile_results", [])
            if item.get("status") == "passed" and item.get("roundtrip_matches") is True
        ]
        chosen = passing[0] if passing else None
        parse_status = "passed" if chosen else "review_required"
        profile = chosen.get("profile") if chosen else None
        canonical_hash = None
        canonical_key = f"canonical-usx/{source_id}/{name}.xml"
        if chosen:
            # Reparse and canonicalise the same source under the passing profile.
            root, parser_meta = converter.parse_input(source_path, "usfm", profile)
            canonical_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            canonical_hash = digest(canonical_bytes)
            local_canonical = canonical_dir / (digest(name.encode())[:16] + ".xml")
            local_canonical.write_bytes(canonical_bytes)
            profile_counts[profile] = profile_counts.get(profile, 0) + 1
            if inclusion == "included":
                code = next(iter(set(book_ids)))
                if code in included_books:
                    raise BatchError(f"Duplicate canonical book assignment: {code}")
                if len(book_ids) != 1:
                    raise BatchError(f"Included member must contain exactly one book: {name}")
                included_books.add(code)
                converted = converter.USXConverter(
                    registry=registry, edition_id=edition_id, source_id=source_id,
                    source_member=name, source_sha256=member_sha,
                    parser=parser_meta,
                ).convert(root)
                errors = converter.validate_output(converted)
                if errors:
                    raise BatchError(f"Converted structure failed validation for {name}: {len(errors)} issue(s).")
                out_rel = f"converted/{code}.json"
                (output_root / out_rel).write_text(
                    json.dumps(converted, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
            else:
                out_rel = None
        else:
            out_rel = None
        member = {
            "member_name": name,
            "sha256": member_sha,
            "book_ids": book_ids,
            "parse_status": parse_status,
            "roundtrip_matches": bool(chosen),
            "compatibility_profile": profile or "2.5",
            "canonical_usx_object_key": canonical_key,
            "canonical_usx_sha256": canonical_hash or "0" * 64,
            "canonical_usx_object_status": "pending",
            "inclusion_status": inclusion,
        }
        if inclusion == "excluded":
            member["excluded_from_publication"] = True
            member["exclusion_reason"] = exclusion_reason
        else:
            member["conversion_output"] = out_rel
        members.append(member)

    missing = sorted(CORE_66 - included_books)
    if missing:
        raise BatchError("Batch did not convert all 66 unique core books: " + ", ".join(missing))
    if set(semantic_index) != {row["member_name"] for row in inventory}:
        raise BatchError("Semantic audit inventory does not exactly match source archive inventory.")
    if len(members) != archive_meta.get("usfm_member_count"):
        raise BatchError("Archive inventory count does not match source-audit summary.")

    profiles = set(profile_counts)
    if len(profiles) != 1:
        raise BatchError("A single parser compatibility profile is required for this manifest.")
    profile = next(iter(profiles))
    manifest = {
        "schema_version": 1,
        "edition_id": edition_id,
        "source_id": source_id,
        "territory": territory,
        "required_permissions": ["display", "cache", "transform"],
        "source_archive": {
            "url": official_url,
            "sha256": archive_meta.get("sha256"),
            "size_bytes": archive_meta.get("size_bytes"),
            "zip_integrity_status": "passed" if source_audit.get("status") in {"core_66_present", "passed"} and archive_meta.get("zip_crc_test") == "passed" else "review_required",
            "signature_verification": {"status": "not_verified"},
        },
        "parser": {
            "package": "usfmtc", "version": PARSER_VERSION,
            "compatibility_profile": profile, "publisher_declared_version": None,
        },
        "converter": CONVERTER_META,
        "expected": {
            "member_count": len(members), "included_member_count": len(included_books),
            "require_all_protestant_66": True,
        },
        "archive_members": members,
        "versification": {
            "scheme_code": f"{source_id}-native-unreviewed",
            "mode": "native_source_only", "status": "review_required",
            "approval": {},
            "excluded_pending_proposal_ids": [],
        },
        "storage": {
            "private_bucket": False,
            "archive_object_status": "pending",
            "canonical_usx_objects_status": "pending",
        },
        "batch": {
            "converted_book_count": len(included_books),
            "excluded_archive_member_count": sum(x["inclusion_status"] == "excluded" for x in members),
            "parser_profile_counts": profile_counts,
            "canonical_usx_local_count": sum(x["roundtrip_matches"] for x in members),
            "canonical_usx_object_status": "pending_remote_verification",
        },
    }
    (output_root / "preflight-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return {
        "status": "batch_complete_preflight_blocked_pending_approvals",
        "source_id": source_id,
        "archive_member_count": len(members),
        "converted_book_count": len(included_books),
        "excluded_member_count": manifest["batch"]["excluded_archive_member_count"],
        "profile_counts": profile_counts,
        "manifest": str(output_root / "preflight-manifest.json"),
        "scripture_text_outputs_private": True,
        "remote_storage_written": False,
        "database_written": False,
        "publication_performed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", required=True, choices=sorted(SOURCES))
    parser.add_argument("--source-audit", type=Path, required=True)
    parser.add_argument("--semantic-audit", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True, help="Extracted directory for the selected source, e.g. .../engwebp")
    parser.add_argument("--registry", type=Path, default=ROOT / "data/usfm/marker-registry.json")
    parser.add_argument("--output-root", type=Path, required=True, help="New private directory; must not already exist")
    parser.add_argument("--territory", default="IN")
    args = parser.parse_args()
    try:
        result = run_batch(
            source_id=args.source_id,
            source_audit=load_json(args.source_audit),
            semantic_audit=load_json(args.semantic_audit),
            source_root=args.source_root,
            registry_path=args.registry,
            output_root=args.output_root,
            territory=args.territory,
        )
        print(json.dumps(result, indent=2))
        return 0
    except (BatchError, converter.ConversionError, OSError, ValueError) as exc:
        print(f"Batch conversion blocked: {type(exc).__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
