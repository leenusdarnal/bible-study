"""Synthetic tests for fail-closed Scripture import preflight."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools"))

from scripture_import_preflight import CORE_66, run_preflight  # noqa: E402
from usfm_to_structured_content import USXConverter  # noqa: E402


def synthetic_registry():
    registry = json.loads((ROOT / "data/usfm/marker-registry.json").read_text(encoding="utf-8"))
    registry["coverage"] = {
        "status": "complete",
        "review_status": "reviewed",
        "note": "Synthetic test-only approval; not a project approval.",
    }
    for entry in registry["markers"]:
        entry["review_status"] = "reviewed"
    registry["_index"] = {entry["marker"]: entry for entry in registry["markers"]}
    return registry


def synthetic_rights(archive_sha):
    return {
        "schema_version": 1,
        "editions": [{
            "schema_version": 1,
            "edition_id": "WEBP",
            "display_name": "Synthetic test edition",
            "source_url": "https://example.test/edition",
            "rights_holder": "Synthetic fixture",
            "rights_status": "approved",
            "territories": ["IN"],
            "permissions": {
                "display": True,
                "cache": True,
                "redistribute": False,
                "transform": False,
                "ai_use": False,
            },
            "evidence": [{
                "kind": "source_archive",
                "reference": "Synthetic-only fixture",
                "sha256": archive_sha,
            }],
            "review": {
                "reviewer": "Synthetic test reviewer",
                "reviewed_at": "2026-11-18",
                "decision_reference": "TEST-APPROVAL-001",
            },
        }],
    }


def synthetic_proposal(archive_sha):
    return {
        "schema_version": 1,
        "proposal_id": "synthetic-pending-move",
        "status": "pending_human_review",
        "from_edition": {
            "source_id": "engwebp",
            "archive_sha256": archive_sha,
        },
        "to_edition": {
            "source_id": "eng-kjv",
            "archive_sha256": "c" * 64,
        },
        "review": {"review_status": "pending", "requires_human_approval": True},
    }


class ScriptureImportPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temp.name)
        cls.output_dir = cls.base / "converted"
        cls.output_dir.mkdir()
        cls.registry = synthetic_registry()
        cls.archive_sha = "b" * 64
        cls.rights = synthetic_rights(cls.archive_sha)
        cls.proposals_dir = cls.base / "proposals"
        cls.proposals_dir.mkdir()
        (cls.proposals_dir / "synthetic-pending.json").write_text(
            json.dumps(synthetic_proposal(cls.archive_sha)), encoding="utf-8"
        )

        members = []
        for book_code in sorted(CORE_66):
            source_member = f"synthetic/{book_code}.usfm"
            source_bytes = (
                f"\\id {book_code}\n\\c 1\n\\p\n\\v 1 Synthetic test text.\n"
            ).encode("utf-8")
            digest = hashlib.sha256(source_bytes).hexdigest()
            root_xml = (
                f'<usx version="2.5"><book code="{book_code}" style="id">'
                f'{book_code}</book><chapter number="1" style="c"/>'
                f'<para style="p"><verse number="1" style="v"/>Synthetic test text.</para>'
                f'</usx>'
            )
            converted = USXConverter(
                registry=cls.registry,
                edition_id="WEBP",
                source_id="engwebp",
                source_member=source_member,
                source_sha256=digest,
                parser={
                    "package": "usfmtc",
                    "version": "0.4.10",
                    "compatibility_profile": "2.5",
                    "publisher_declared_version": None,
                },
            ).convert(__import__("xml.etree.ElementTree", fromlist=["ElementTree"]).fromstring(root_xml))
            destination = cls.output_dir / f"{book_code}.json"
            destination.write_text(json.dumps(converted, ensure_ascii=False), encoding="utf-8")
            members.append({
                "member_name": source_member,
                "sha256": digest,
                "book_ids": [book_code],
                "parse_status": "passed",
                "roundtrip_matches": True,
                "compatibility_profile": "2.5",
                "conversion_output": f"converted/{book_code}.json",
            })

        cls.manifest = {
            "schema_version": 1,
            "edition_id": "WEBP",
            "source_id": "engwebp",
            "territory": "IN",
            "source_archive": {
                "url": "https://example.test/engwebp_usfm.zip",
                "sha256": cls.archive_sha,
                "size_bytes": 1024,
                "zip_integrity_status": "passed",
                "signature_verification": {"status": "verified"},
            },
            "parser": {
                "package": "usfmtc",
                "version": "0.4.10",
                "compatibility_profile": "2.5",
                "publisher_declared_version": None,
            },
            "converter": {
                "name": "bible-study-usfm-structured-converter",
                "version": "0.1.0",
            },
            "expected": {
                "member_count": len(CORE_66),
                "require_all_protestant_66": True,
            },
            "archive_members": members,
            "versification": {
                "scheme_code": "synthetic-webp-source-v1",
                "mode": "native_source_only",
                "status": "approved",
                "approval": {
                    "reviewer": "Synthetic reviewer",
                    "reviewed_at": "2026-11-18",
                    "decision_reference": "TEST-VERSIFICATION-001",
                },
                "excluded_pending_proposal_ids": ["synthetic-pending-move"],
            },
            "storage": {
                "private_bucket": True,
                "archive_object_status": "verified",
                "canonical_usx_objects_status": "verified",
            },
        }

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.manifest = copy.deepcopy(self.manifest)
        self.rights = copy.deepcopy(self.rights)
        self.registry = copy.deepcopy(self.registry)

    def run_check(self):
        return run_preflight(
            self.manifest,
            self.rights,
            self.registry,
            base_dir=self.base,
            proposals_dir=self.proposals_dir,
        )

    def findings(self, report):
        return {item["code"] for item in report["findings"]}

    def replace_output(self, book_code, mutate):
        path = self.base / "converted" / f"{book_code}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        mutate(data)
        replacement = self.base / "converted" / f"{book_code}-changed.json"
        replacement.write_text(json.dumps(data), encoding="utf-8")
        for member in self.manifest["archive_members"]:
            if member["book_ids"] == [book_code]:
                member["conversion_output"] = f"converted/{book_code}-changed.json"
                break

    def test_complete_synthetic_package_passes_all_preflight_gates(self):
        report = self.run_check()
        self.assertEqual(report["status"], "passed")
        self.assertTrue(report["ready_for_import"])
        self.assertEqual(report["summary"]["core_book_count"], 66)
        self.assertEqual(report["summary"]["converted_member_count"], 66)
        self.assertEqual(report["summary"]["verse_projection_count"], 66)
        self.assertIn("synthetic-pending-move", report["summary"]["pending_versification_proposal_ids"])

    def test_actual_pending_rights_register_is_blocked(self):
        actual = json.loads((ROOT / "data/rights/translation-rights-register.json").read_text(encoding="utf-8"))
        report = run_preflight(
            self.manifest, actual, self.registry,
            base_dir=self.base, proposals_dir=self.proposals_dir,
        )
        self.assertFalse(report["ready_for_import"])
        self.assertIn("RIGHTS_NOT_APPROVED", self.findings(report))

    def test_archive_member_omission_breaks_expected_coverage_and_canon(self):
        self.manifest["archive_members"].pop()
        self.manifest["expected"]["member_count"] -= 1
        report = self.run_check()
        self.assertIn("CORE_CANON_INCOMPLETE", self.findings(report))
        self.assertIn("CONVERSION_COVERAGE_INCOMPLETE", self.findings(report))

    def test_hash_mismatch_between_manifest_and_conversion_is_blocked(self):
        self.replace_output("GEN", lambda data: data["source"].update({"source_sha256": "d" * 64}))
        report = self.run_check()
        self.assertIn("CONVERSION_SOURCE_MISMATCH", self.findings(report))

    def test_unreviewed_marker_registry_is_blocked(self):
        self.registry["coverage"]["status"] = "initial_partial"
        report = self.run_check()
        self.assertIn("MARKER_REGISTRY_NOT_APPROVED", self.findings(report))

    def test_unknown_marker_in_conversion_is_blocked(self):
        self.replace_output("GEN", lambda data: data.update({"unresolved_markers": ["zunknown"]}))
        report = self.run_check()
        self.assertIn("CONVERTER_UNRESOLVED_MARKERS", self.findings(report))

    def test_pending_cross_edition_mapping_blocks_cross_edition_mode(self):
        self.manifest["versification"]["mode"] = "cross_edition"
        report = self.run_check()
        self.assertIn("PENDING_MAPPING_APPLICABLE", self.findings(report))

    def test_pending_mapping_must_be_explicitly_excluded_for_native_import(self):
        self.manifest["versification"]["excluded_pending_proposal_ids"] = []
        report = self.run_check()
        self.assertIn("PENDING_MAPPING_NOT_EXPLICITLY_EXCLUDED", self.findings(report))

    def test_storage_must_be_private_and_checksum_verified(self):
        self.manifest["storage"]["private_bucket"] = False
        self.manifest["storage"]["canonical_usx_objects_status"] = "pending"
        report = self.run_check()
        self.assertIn("STORAGE_NOT_PRIVATE", self.findings(report))
        self.assertIn("CANONICAL_USX_OBJECTS_NOT_VERIFIED", self.findings(report))

    def test_annotation_only_state_must_not_contain_verse_text(self):
        self.replace_output(
            "GEN",
            lambda data: data["verse_projections"][0].update({
                "content_state": "annotation_only",
                "annotation_count": 1,
            }),
        )
        report = self.run_check()
        self.assertIn("CONTENT_STATE_INVALID", self.findings(report))

    def test_unverified_signature_is_blocked(self):
        self.manifest["source_archive"]["signature_verification"] = {"status": "not_verified"}
        report = self.run_check()
        self.assertIn("ARCHIVE_SIGNATURE_UNVERIFIED", self.findings(report))

    def test_explicit_signature_waiver_is_a_warning_not_a_silent_pass(self):
        self.manifest["source_archive"]["signature_verification"] = {
            "status": "waived",
            "reviewer": "Synthetic security reviewer",
            "decision_reference": "TEST-SIGNATURE-WAIVER",
        }
        report = self.run_check()
        self.assertTrue(report["ready_for_import"])
        self.assertEqual(report["summary"]["warning_count"], 1)
        self.assertIn("ARCHIVE_SIGNATURE_WAIVED", self.findings(report))

    def test_rights_checksum_must_match_exact_archive(self):
        self.rights["editions"][0]["evidence"][0]["sha256"] = "e" * 64
        report = self.run_check()
        self.assertIn("RIGHTS_ARCHIVE_EVIDENCE_MISMATCH", self.findings(report))

    def test_rights_territory_must_be_explicit(self):
        self.rights["editions"][0]["territories"] = ["GB"]
        report = self.run_check()
        self.assertIn("RIGHTS_TERRITORY_NOT_APPROVED", self.findings(report))

    def test_report_never_contains_synthetic_verse_text(self):
        report = self.run_check()
        serialized = json.dumps(report)
        self.assertNotIn("Synthetic test text.", serialized)

    def test_invalid_source_reference_is_blocked(self):
        self.replace_output(
            "GEN",
            lambda data: data["verse_projections"][0].update({"verse_label": ""}),
        )
        report = self.run_check()
        self.assertIn("VERSE_REFERENCE_MALFORMED", self.findings(report))


if __name__ == "__main__":
    unittest.main()
