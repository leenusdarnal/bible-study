from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from scripture_import_staging_coordinator import CoordinationError, coordinate  # noqa: E402


class StagingCoordinatorTests(unittest.TestCase):
    def _inputs(self, base: Path):
        manifest = {
            "schema_version": 1,
            "edition_id": "WEBP",
            "source_id": "engwebp",
            "territory": "IN",
            "source_archive": {"sha256": "a" * 64},
        }
        rights = {"schema_version": 1, "editions": []}
        registry = {"schema_version": 1, "registry_version": "synthetic", "markers": [], "coverage": {}}
        manifest_path = base / "manifest.json"
        rights_path = base / "rights.json"
        registry_path = base / "registry.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        rights_path.write_text(json.dumps(rights), encoding="utf-8")
        registry_path.write_text(json.dumps(registry), encoding="utf-8")
        return manifest_path, rights_path, registry_path

    def test_incomplete_manifest_produces_blocked_metadata_handoff(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            manifest, rights, registry = self._inputs(base)
            output = base / "run-record"
            result = coordinate(
                manifest_path=manifest,
                rights_path=rights,
                registry_path=registry,
                proposals_dir=None,
                output_dir=output,
            )
            self.assertEqual(result["handoff_status"], "blocked")
            self.assertFalse(result["d1_written"])
            self.assertFalse(result["r2_written"])
            handoff = json.loads((output / "staging-handoff.json").read_text(encoding="utf-8"))
            self.assertEqual(handoff["state"], "validation_blocked")
            self.assertFalse(handoff["controls"]["publication_authorized"])
            serialized = json.dumps(handoff)
            self.assertNotIn("In the beginning", serialized)

    def test_existing_output_directory_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            manifest, rights, registry = self._inputs(base)
            output = base / "run-record"
            output.mkdir()
            sentinel = output / "keep.txt"
            sentinel.write_text("immutable", encoding="utf-8")
            with self.assertRaises(CoordinationError):
                coordinate(
                    manifest_path=manifest,
                    rights_path=rights,
                    registry_path=registry,
                    proposals_dir=None,
                    output_dir=output,
                )
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "immutable")

    def test_same_inputs_have_stable_run_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            manifest, rights, registry = self._inputs(base)
            first = coordinate(
                manifest_path=manifest, rights_path=rights, registry_path=registry,
                proposals_dir=None, output_dir=base / "run-one",
            )
            second = coordinate(
                manifest_path=manifest, rights_path=rights, registry_path=registry,
                proposals_dir=None, output_dir=base / "run-two",
            )
            self.assertEqual(first["run_id"], second["run_id"])


if __name__ == "__main__":
    unittest.main()
