"""Regression tests for explicit translation-text content states."""

from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS = [
    ROOT / "docs/sql/0001_scripture_core.sql",
    ROOT / "docs/sql/0002_seed_protestant_66.sql",
    ROOT / "docs/sql/0003_reading_progress.sql",
    ROOT / "docs/sql/0004_versification_mapping_groups.sql",
    ROOT / "docs/sql/0005_translation_text_content_states.sql",
]


class TranslationTextContentStateMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys = ON")
        for migration in MIGRATIONS:
            self.db.executescript(migration.read_text(encoding="utf-8"))

        self.db.execute(
            """
            INSERT INTO versification_schemes
              (id, code, name, status, created_at, updated_at)
            VALUES ('scheme-test', 'scheme-test', 'Test scheme',
                    'verified', 1, 1)
            """
        )
        self.db.execute(
            """
            INSERT INTO scheme_chapters
              (id, scheme_id, work_id, chapter_label, chapter_order)
            VALUES ('chapter-gen-1', 'scheme-test', 'work-gen', '1', 1)
            """
        )
        for number in range(1, 5):
            self.db.execute(
                """
                INSERT INTO scripture_units
                  (id, scheme_id, work_id, chapter_id, unit_label, unit_order, unit_kind)
                VALUES (?, 'scheme-test', 'work-gen', 'chapter-gen-1', ?, ?, 'verse')
                """,
                (f"unit-gen-1-{number}", str(number), number),
            )
        self.db.execute(
            """
            INSERT INTO translation_editions
              (id, code, name, abbreviation, language_tag,
               versification_scheme_id, created_at, updated_at)
            VALUES ('edition-test', 'test', 'Synthetic test edition',
                    'TST', 'en', 'scheme-test', 1, 1)
            """
        )

    def tearDown(self) -> None:
        self.db.close()

    def insert_text(
        self,
        row_id: str,
        unit_number: int,
        text: str,
        content_state: str = "text",
        footnotes: str | None = None,
    ) -> None:
        self.db.execute(
            """
            INSERT INTO translation_texts
              (id, edition_id, versification_scheme_id, scripture_unit_id,
               text, footnote_metadata_json, content_state, created_at, updated_at)
            VALUES (?, 'edition-test', 'scheme-test', ?, ?, ?, ?, 1, 1)
            """,
            (
                row_id,
                f"unit-gen-1-{unit_number}",
                text,
                footnotes,
                content_state,
            ),
        )

    def test_text_bearing_unit_can_also_carry_footnotes(self) -> None:
        self.insert_text(
            "text-with-note",
            1,
            "Synthetic verse wording.",
            footnotes='{"footnotes":[{"marker":"f"}]}',
        )
        row = self.db.execute(
            "SELECT text, content_state FROM translation_texts WHERE id = ?",
            ("text-with-note",),
        ).fetchone()
        self.assertEqual(row, ("Synthetic verse wording.", "text"))

    def test_annotation_only_source_anchor_is_valid(self) -> None:
        self.insert_text(
            "note-only",
            2,
            "",
            content_state="annotation_only",
            footnotes='{"footnotes":[{"marker":"f","body":"synthetic note"}]}',
        )
        row = self.db.execute(
            "SELECT text, content_state, footnote_metadata_json "
            "FROM translation_texts WHERE id = ?",
            ("note-only",),
        ).fetchone()
        self.assertEqual(row[0:2], ("", "annotation_only"))
        self.assertIsNotNone(row[2])

    def test_explicit_empty_source_marker_is_valid(self) -> None:
        self.insert_text(
            "empty-marker",
            3,
            "",
            content_state="empty_marker",
        )
        row = self.db.execute(
            "SELECT text, content_state, footnote_metadata_json "
            "FROM translation_texts WHERE id = ?",
            ("empty-marker",),
        ).fetchone()
        self.assertEqual(row, ("", "empty_marker", None))

    def test_default_text_state_rejects_blank_text(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_text("invalid-default", 4, "")

    def test_annotation_only_requires_note_metadata_and_no_text(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_text("missing-note", 4, "", content_state="annotation_only")
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_text(
                "note-and-text",
                4,
                "Unexpected text",
                content_state="annotation_only",
                footnotes='{"footnotes":[]}',
            )

    def test_empty_marker_rejects_text_or_note_metadata(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_text(
                "empty-with-text",
                4,
                "Unexpected text",
                content_state="empty_marker",
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_text(
                "empty-with-note",
                4,
                "",
                content_state="empty_marker",
                footnotes='{"footnotes":[]}',
            )

    def test_update_cannot_remove_note_from_annotation_only_anchor(self) -> None:
        self.insert_text(
            "update-note-only",
            2,
            "",
            content_state="annotation_only",
            footnotes='{"footnotes":[{"marker":"f"}]}',
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "UPDATE translation_texts SET footnote_metadata_json = NULL "
                "WHERE id = 'update-note-only'"
            )

    def test_invalid_content_state_is_rejected(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_text(
                "invalid-state",
                4,
                "Synthetic wording",
                content_state="unknown",
            )

    def test_foreign_key_integrity_is_preserved(self) -> None:
        self.assertEqual(
            self.db.execute("PRAGMA foreign_key_check").fetchall(),
            [],
        )


if __name__ == "__main__":
    unittest.main()
