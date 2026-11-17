"""Unit tests for the metadata-only USFM source archive auditor."""
from __future__ import annotations

import io
import sys
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import scripture_source_audit as audit  # noqa: E402


def make_zip(entries: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, text in entries.items():
            archive.writestr(name, text.encode("utf-8"))
    return buffer.getvalue()


class UsfmParserTests(unittest.TestCase):
    def test_parses_version_book_chapters_verses_ranges_and_markers(self):
        source = r"""\usfm 3.0
\ide UTF-8
\id GEN Genesis
\h Genesis
\c 1
\p
\v 1 First verse.
\v 2-3 Combined verses.
\c 2
\v 1 Another chapter.
"""
        parsed = audit.parse_usfm_text(source, "GEN.usfm")
        self.assertEqual(parsed["usfm_versions"], ["3.0"])
        self.assertEqual(parsed["book_ids_in_member"], ["GEN"])
        self.assertEqual(len(parsed["books"]["GEN"]["chapters"]), 2)
        self.assertEqual(parsed["books"]["GEN"]["verse_marker_count"], 3)
        self.assertEqual(
            parsed["books"]["GEN"]["verse_address_occurrences"],
            [("1", "1"), ("1", "2-3"), ("2", "1")],
        )
        self.assertEqual(parsed["books"]["GEN"]["verse_range_marker_count"], 1)
        self.assertGreaterEqual(parsed["marker_counts"]["v"], 3)

    def test_reports_no_version_marker_without_inventing_one(self):
        parsed = audit.parse_usfm_text(r"\id GEN Genesis" + "\n" + r"\c 1" + "\n" + r"\v 1 Text")
        self.assertEqual(parsed["usfm_versions"], [])
        self.assertIn("GEN", parsed["books"])


class ArchiveAuditTests(unittest.TestCase):
    def test_audits_archive_and_reports_missing_core_books(self):
        data = make_zip({
            "GEN.usfm": r"\usfm 3.0" + "\n" + r"\id GEN Genesis" + "\n" + r"\c 1" + "\n" + r"\v 1 Text",
            "MAT.usfm": r"\usfm 3.0" + "\n" + r"\id MAT Matthew" + "\n" + r"\c 1" + "\n" + r"\v 1 Text",
        })
        report = audit.inspect_archive_bytes(data, "engwebp")
        self.assertEqual(report["archive"]["zip_crc_test"], "passed")
        self.assertEqual(report["archive"]["usfm_member_count"], 2)
        self.assertEqual(report["parse_summary"]["book_id_count"], 2)
        self.assertEqual(report["status"], "review_required")
        self.assertIn("GEN", [b["book_id"] for b in report["book_inventory"]])

    def test_accepts_complete_core_book_identity_set(self):
        lines = [r"\usfm 3.0"]
        for book_id in sorted(audit.EXPECTED_CORE_BOOKS):
            lines.extend([rf"\id {book_id} {book_id}", r"\c 1", r"\v 1 Sample"])
        data = make_zip({"all-books.usfm": "\n".join(lines)})
        report = audit.inspect_archive_bytes(data, "engwebp")
        self.assertEqual(report["status"], "core_66_present")
        self.assertEqual(report["parse_summary"]["core_66_book_ids_found"], 66)
        self.assertEqual(report["parse_summary"]["missing_core_book_ids"], [])
        self.assertEqual(report["parse_summary"]["total_chapter_count"], 66)

    def test_reports_duplicate_verse_addresses(self):
        usfm = r"\id GEN Genesis" + "\n" + r"\c 1" + "\n" + r"\v 1 Text A" + "\n" + r"\v 1 Text B"
        data = make_zip({"GEN.usfm": usfm})
        report = audit.inspect_archive_bytes(data, "engwebp")
        genesis = next(row for row in report["book_inventory"] if row["book_id"] == "GEN")
        self.assertEqual(genesis["verse_marker_count"], 2)
        self.assertEqual(genesis["distinct_chapter_verse_labels"], 1)
        self.assertEqual(genesis["duplicate_chapter_verse_labels"], 1)

    def test_writes_exact_address_comparison_without_verse_text(self):
        import json
        import tempfile

        reports = [
            {
                "source_id": "engwebp",
                "verse_address_inventory": [
                    {"book_id": "ROM", "chapter_label": "16", "verse_label": "1"},
                    {"book_id": "ROM", "chapter_label": "16", "verse_label": "2"},
                ],
                "member_inventory": [],
                "book_inventory": [],
                "parse_summary": {"marker_counts": {}},
            },
            {
                "source_id": "eng-kjv",
                "verse_address_inventory": [
                    {"book_id": "ROM", "chapter_label": "16", "verse_label": "1"},
                ],
                "member_inventory": [],
                "book_inventory": [],
                "parse_summary": {"marker_counts": {}},
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            audit.write_outputs(reports, Path(tmp))
            manifest = json.loads((Path(tmp) / "audit-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["primary_versification_address_comparison"]["common_addresses"], 1)
            self.assertEqual(manifest["primary_versification_address_comparison"]["webp_only"], [
                {"book_id": "ROM", "chapter_label": "16", "verse_label": "2"}
            ])
            self.assertEqual(manifest["primary_versification_address_comparison"]["kjv_only"], [])
            diff = (Path(tmp) / "verse-address-differences.csv").read_text(encoding="utf-8")
            self.assertIn("ROM,16,2,True,False", diff)
            self.assertNotIn("Text A", diff)

    def test_rejects_path_traversal_member(self):
        data = make_zip({"../escape.usfm": r"\id GEN Genesis" + "\n" + r"\c 1" + "\n" + r"\v 1 Text"})
        with self.assertRaises(audit.AuditError):
            audit.inspect_archive_bytes(data, "engwebp")

    def test_rejects_invalid_zip(self):
        with self.assertRaises(audit.AuditError):
            audit.inspect_archive_bytes(b"not a zip", "engwebp")

    def test_rejects_non_utf8_usfm_member(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("GEN.usfm", b"\xff\xfe\xfa")
        with self.assertRaises(audit.AuditError):
            audit.inspect_archive_bytes(buffer.getvalue(), "engwebp")


if __name__ == "__main__":
    unittest.main()
