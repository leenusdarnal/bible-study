#!/usr/bin/env python3
"""Synthetic-only SQLite staging adapter; never connects to Cloudflare D1 or R2."""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


class StagingError(RuntimeError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class SyntheticStagingAdapter:
    """Transactional test harness for staging contracts, backed by caller-owned SQLite."""

    def __init__(self, connection: sqlite3.Connection):
        self.db = connection
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS synthetic_runs (
              run_id TEXT PRIMARY KEY,
              source_fingerprint TEXT NOT NULL,
              state TEXT NOT NULL CHECK (state IN ('staged','validated','rolled_back'))
            );
            CREATE TABLE IF NOT EXISTS synthetic_units (
              run_id TEXT NOT NULL REFERENCES synthetic_runs(run_id) ON DELETE CASCADE,
              unit_key TEXT NOT NULL,
              payload_hash TEXT NOT NULL,
              PRIMARY KEY (run_id, unit_key)
            );
        """)

    @staticmethod
    def _validate(run_id: str, source_fingerprint: str, units: list[dict[str, Any]]) -> None:
        if not run_id.startswith("synthetic-"):
            raise StagingError("Only synthetic-* run IDs are accepted.")
        if not source_fingerprint.startswith("synthetic:"):
            raise StagingError("Only synthetic source fingerprints are accepted.")
        if not units:
            raise StagingError("At least one synthetic unit is required.")
        seen: set[str] = set()
        for unit in units:
            if set(unit) != {"unit_key", "fixture_value"}:
                raise StagingError("Unit schema must contain only unit_key and fixture_value.")
            key = unit["unit_key"]
            value = unit["fixture_value"]
            if not isinstance(key, str) or not key.startswith("fixture:") or key in seen:
                raise StagingError("Unit keys must be unique fixture:* identifiers.")
            if not isinstance(value, str) or not value.startswith("SYNTHETIC_FIXTURE_"):
                raise StagingError("Only synthetic fixture values are accepted.")
            seen.add(key)

    def stage(self, run_id: str, source_fingerprint: str, units: list[dict[str, Any]], *, fail_after: int | None = None) -> dict[str, Any]:
        self._validate(run_id, source_fingerprint, units)
        source_hash = hashlib.sha256(source_fingerprint.encode()).hexdigest()
        try:
            with self.db:
                existing = self.db.execute(
                    "SELECT source_fingerprint, state FROM synthetic_runs WHERE run_id=?", (run_id,)
                ).fetchone()
                if existing:
                    if existing != (source_hash, "staged"):
                        raise StagingError("Run ID already exists with different source or state.")
                    stored = self.db.execute(
                        "SELECT unit_key, payload_hash FROM synthetic_units WHERE run_id=? ORDER BY unit_key", (run_id,)
                    ).fetchall()
                    expected = sorted((u["unit_key"], hashlib.sha256(u["fixture_value"].encode()).hexdigest()) for u in units)
                    if stored != expected:
                        raise StagingError("Idempotency conflict: replay payload differs from stored units.")
                    return {"status": "already_staged", "unit_count": len(stored)}
                self.db.execute(
                    "INSERT INTO synthetic_runs(run_id, source_fingerprint, state) VALUES(?,?, 'staged')",
                    (run_id, source_hash),
                )
                for index, unit in enumerate(units, start=1):
                    digest = hashlib.sha256(unit["fixture_value"].encode()).hexdigest()
                    self.db.execute(
                        "INSERT INTO synthetic_units(run_id, unit_key, payload_hash) VALUES(?,?,?)",
                        (run_id, unit["unit_key"], digest),
                    )
                    if fail_after == index:
                        raise StagingError("Injected failure to verify transaction rollback.")
        except sqlite3.IntegrityError as exc:
            raise StagingError("Staging constraint conflict.") from exc
        return {"status": "staged", "unit_count": len(units)}

    def rollback(self, run_id: str) -> None:
        with self.db:
            row = self.db.execute("SELECT state FROM synthetic_runs WHERE run_id=?", (run_id,)).fetchone()
            if row is None:
                raise StagingError("Unknown synthetic run.")
            self.db.execute("DELETE FROM synthetic_runs WHERE run_id=?", (run_id,))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run synthetic-only in-memory contract check.")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("This adapter only supports --self-test; it has no live database mode.")
    db = sqlite3.connect(":memory:")
    adapter = SyntheticStagingAdapter(db)
    result = adapter.stage("synthetic-smoke", "synthetic:smoke", [
        {"unit_key": "fixture:one", "fixture_value": "SYNTHETIC_FIXTURE_ONE"}
    ])
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
