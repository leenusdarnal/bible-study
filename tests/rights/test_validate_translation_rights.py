"""Tests for the fail-closed translation rights validator."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from validate_translation_rights import validate_document  # noqa: E402


def approved_record():
    return {
        "schema_version": 1, "edition_id": "TEST", "display_name": "Test Edition",
        "source_url": "https://example.org/source", "rights_holder": "Example",
        "rights_status": "approved", "territories": ["IN"],
        "permissions": {"display": True, "cache": True, "redistribute": False,
                        "transform": "conditional", "ai_use": False},
        "evidence": [{"kind": "licence", "reference": "licence.pdf"}],
        "review": {"reviewer": "Reviewer", "reviewed_at": "2026-11-18",
                   "decision_reference": "LEGAL-001"},
    }


class RightsValidatorTests(unittest.TestCase):
    def test_pending_editions_cannot_pass_publication_gate(self):
        doc = {"schema_version": 1, "editions": [{
            **approved_record(), "rights_status": "review_required",
            "territories": [], "review": {"reviewer": None}
        }]}
        result = validate_document(doc, "IN")
        self.assertFalse(result["valid"])
        self.assertTrue(any("not approved" in x for x in result["errors"]))

    def test_approved_edition_passes_only_for_approved_territory(self):
        doc = {"schema_version": 1, "editions": [approved_record()]}
        self.assertTrue(validate_document(doc, "IN")["valid"])
        self.assertFalse(validate_document(doc, "GB")["valid"])

    def test_approval_requires_evidence_and_named_review(self):
        record = approved_record()
        record["evidence"] = []
        record["review"]["reviewer"] = None
        result = validate_document({"schema_version": 1, "editions": [record]})
        self.assertFalse(result["valid"])

    def test_unknown_permission_values_are_rejected(self):
        record = approved_record()
        record["permissions"]["display"] = "probably"
        result = validate_document({"schema_version": 1, "editions": [record]})
        self.assertFalse(result["valid"])

    def test_duplicate_edition_ids_are_rejected(self):
        record = approved_record()
        result = validate_document({"schema_version": 1, "editions": [record, record]})
        self.assertFalse(result["valid"])


if __name__ == "__main__":
    unittest.main()
