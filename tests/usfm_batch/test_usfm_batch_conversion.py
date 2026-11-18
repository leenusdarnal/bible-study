from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from usfm_batch_conversion import BatchError, classify_member, load_json, run_batch


class BatchOrchestratorTests(unittest.TestCase):
    def test_only_pure_core_members_are_included(self):
        self.assertEqual(classify_member(["GEN"]), ("included", None))
        self.assertEqual(classify_member(["TOB"]), (
            "excluded", "Outside the initial 66-book Protestant canon."
        ))

    def test_front_matter_without_book_id_is_explicitly_excluded(self):
        status, reason = classify_member([])
        self.assertEqual(status, "excluded")
        self.assertIn("Front matter", reason)

    def test_mixed_canon_and_noncanon_member_is_not_silently_split(self):
        status, reason = classify_member(["GEN", "TOB"])
        self.assertEqual(status, "excluded")
        self.assertIn("manual source separation", reason)

    def test_source_identity_mismatch_fails_before_output_creation(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            output = base / "private-output"
            with self.assertRaises(BatchError):
                run_batch(
                    source_id="engwebp",
                    source_audit={"source_id": "eng-kjv"},
                    semantic_audit={"schema_version": 2, "files": []},
                    source_root=base,
                    registry_path=ROOT / "data/usfm/marker-registry.json",
                    output_root=output,
                    territory="IN",
                )
            self.assertFalse(output.exists())

    def test_bad_semantic_audit_schema_is_rejected(self):
        with self.assertRaises(BatchError):
            from usfm_batch_conversion import _semantic_member_index
            _semantic_member_index({"schema_version": 1, "files": []}, "engwebp")


if __name__ == "__main__":
    unittest.main()
