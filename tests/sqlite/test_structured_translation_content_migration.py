"""Regression tests for loss-preserving structured Scripture content."""

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
    ROOT / "docs/sql/0006_structured_translation_content.sql",
]


class StructuredTranslationContentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys = ON")
        for migration in MIGRATIONS:
            self.db.executescript(migration.read_text(encoding="utf-8"))
        self.db.execute(
            """INSERT INTO versification_schemes
               (id, code, name, status, created_at, updated_at)
               VALUES ('scheme-structured', 'structured', 'Structured test', 'verified', 1, 1)"""
        )
        self.db.execute(
            """INSERT INTO scheme_chapters
               (id, scheme_id, work_id, chapter_label, chapter_order)
               VALUES ('chapter-gen-1', 'scheme-structured', 'work-gen', '1', 1)"""
        )
        self.db.execute(
            """INSERT INTO scripture_units
               (id, scheme_id, work_id, chapter_id, unit_label, unit_order, unit_kind)
               VALUES ('unit-gen-1-1', 'scheme-structured', 'work-gen', 'chapter-gen-1', '1', 1, 'verse')"""
        )
        self.db.execute(
            """INSERT INTO translation_editions
               (id, code, name, abbreviation, language_tag, versification_scheme_id, created_at, updated_at)
               VALUES ('edition-structured', 'structured', 'Structured test', 'ST', 'en', 'scheme-structured', 1, 1)"""
        )
        self.db.execute(
            """INSERT INTO translation_texts
               (id, edition_id, versification_scheme_id, scripture_unit_id, text, content_state, created_at, updated_at)
               VALUES ('text-1', 'edition-structured', 'scheme-structured', 'unit-gen-1-1',
                       'Synthetic plain-text projection', 'text', 1, 1)"""
        )
        self.db.execute(
            """INSERT INTO translation_content_blocks
               (id, edition_id, versification_scheme_id, work_id, chapter_id, anchor_unit_id,
                block_order, block_type, source_marker, source_member, source_order, created_at, updated_at)
               VALUES ('block-1', 'edition-structured', 'scheme-structured', 'work-gen',
                       'chapter-gen-1', 'unit-gen-1-1', 1, 'paragraph', '\\p',
                       '01-GEN.usfm', 1, 1, 1)"""
        )

    def tearDown(self) -> None:
        self.db.close()

    def test_nested_inline_nodes_preserve_order_and_attributes(self) -> None:
        self.db.executemany(
            """INSERT INTO translation_content_nodes
               (id, block_id, parent_node_id, node_order_path, node_type, source_marker,
                text_content, attributes_json, source_order, created_at)
               VALUES (?, 'block-1', ?, ?, ?, ?, ?, ?, ?, 1)""",
            [
                ('node-span', None, '0001', 'span', '\\add', None, '{"style":"added"}', 1),
                ('node-text', 'node-span', '0001.0001', 'text', None, 'Synthetic added words', None, 2),
                ('node-note', None, '0002', 'footnote', '\\f', None, '{"caller":"+"}', 3),
            ],
        )
        rows = self.db.execute(
            """SELECT node_type, source_marker, text_content, node_order_path
               FROM translation_content_nodes WHERE block_id = 'block-1'
               ORDER BY node_order_path"""
        ).fetchall()
        self.assertEqual([row[0] for row in rows], ['span', 'text', 'footnote'])
        self.assertEqual(rows[0][1], '\\add')
        self.assertEqual(rows[1][2], 'Synthetic added words')
        self.assertEqual(rows[2][3], '0002')

    def test_nodes_cannot_reference_a_parent_in_another_block(self) -> None:
        self.db.execute(
            """INSERT INTO translation_content_blocks
               (id, edition_id, versification_scheme_id, work_id, chapter_id, block_order,
                block_type, source_member, source_order, created_at, updated_at)
               VALUES ('block-2', 'edition-structured', 'scheme-structured', 'work-gen',
                       'chapter-gen-1', 2, 'paragraph', '01-GEN.usfm', 2, 1, 1)"""
        )
        self.db.execute(
            """INSERT INTO translation_content_nodes
               (id, block_id, node_order_path, node_type, source_order, created_at)
               VALUES ('node-parent', 'block-1', '0001', 'span', 1, 1)"""
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                """INSERT INTO translation_content_nodes
                   (id, block_id, parent_node_id, node_order_path, node_type, source_order, created_at)
                   VALUES ('bad-child', 'block-2', 'node-parent', '0001.0001', 'text', 1, 1)"""
            )

    def test_invalid_json_metadata_is_rejected(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                """INSERT INTO translation_content_nodes
                   (id, block_id, node_order_path, node_type, attributes_json, source_order, created_at)
                   VALUES ('bad-json', 'block-1', '0001', 'span', '{not-json', 1, 1)"""
            )

    def test_duplicate_node_order_path_is_rejected(self) -> None:
        self.db.execute(
            """INSERT INTO translation_content_nodes
               (id, block_id, node_order_path, node_type, source_order, created_at)
               VALUES ('node-first', 'block-1', '0001', 'text', 1, 1)"""
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                """INSERT INTO translation_content_nodes
                   (id, block_id, node_order_path, node_type, source_order, created_at)
                   VALUES ('node-duplicate', 'block-1', '0001', 'text', 2, 1)"""
            )

    def test_book_level_blocks_do_not_require_a_chapter(self) -> None:
        self.db.execute(
            """INSERT INTO translation_content_blocks
               (id, edition_id, versification_scheme_id, work_id, block_order,
                block_type, source_member, source_order, created_at, updated_at)
               VALUES ('book-intro', 'edition-structured', 'scheme-structured', 'work-gen',
                       1, 'book_intro', '01-GEN.usfm', 2, 1, 1)"""
        )
        self.assertEqual(
            self.db.execute("SELECT chapter_id FROM translation_content_blocks WHERE id = 'book-intro'").fetchone()[0],
            None,
        )


if __name__ == "__main__":
    unittest.main()
