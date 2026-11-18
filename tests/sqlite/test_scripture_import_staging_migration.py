"""Regression tests for the Scripture import staging and publication migration."""

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
    ROOT / "docs/sql/0007_scripture_import_staging.sql",
]


class ScriptureImportStagingMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys = ON")
        for migration in MIGRATIONS:
            self.db.executescript(migration.read_text(encoding="utf-8"))

        self.db.execute(
            """
            INSERT INTO versification_schemes
              (id, code, name, status, created_at, updated_at)
            VALUES ('scheme-import', 'scheme-import', 'Import test scheme',
                    'verified', 1, 1)
            """
        )
        self.db.execute(
            """
            INSERT INTO scheme_chapters
              (id, scheme_id, work_id, chapter_label, chapter_order)
            VALUES ('chapter-import-gen-1', 'scheme-import', 'work-gen', '1', 1)
            """
        )
        self.db.execute(
            """
            INSERT INTO scripture_units
              (id, scheme_id, work_id, chapter_id, unit_label, unit_order, unit_kind)
            VALUES ('unit-import-gen-1-1', 'scheme-import', 'work-gen',
                    'chapter-import-gen-1', '1', 1, 'verse')
            """
        )
        self.db.execute(
            """
            INSERT INTO translation_editions
              (id, code, name, abbreviation, language_tag,
               versification_scheme_id, created_at, updated_at)
            VALUES ('edition-import', 'imp', 'Import test edition',
                    'IMP', 'en', 'scheme-import', 1, 1)
            """
        )

    def tearDown(self) -> None:
        self.db.close()

    def create_run(self, run_id: str = "run-1", archive_sha: str = "a" * 64) -> None:
        self.db.execute(
            """
            INSERT INTO scripture_import_runs (
              id, edition_id, versification_scheme_id,
              source_archive_url, source_archive_object_key,
              source_archive_sha256, source_archive_size_bytes, source_retrieved_at,
              parser_name, parser_version, parser_compatibility_profile,
              manifest_json, created_at, updated_at
            ) VALUES (
              ?, 'edition-import', 'scheme-import',
              'https://source.example/archive.zip',
              'source-archives/edition-import/sha.zip',
              ?, 100, 1000, 'usfmtc', '0.4.10', '2.5',
              '{"schema_version":1}', 1000, 1000
            )
            """,
            (run_id, archive_sha),
        )

    def create_file(self, run_id: str = "run-1", file_id: str = "file-gen") -> None:
        self.db.execute(
            """
            INSERT INTO scripture_import_files (
              id, import_run_id, member_name, member_sha256,
              member_size_bytes, book_code, work_id, created_at, updated_at
            ) VALUES (
              ?, ?, '02-GEN.usfm', ?, 50, 'GEN', 'work-gen', 1000, 1000
            )
            """,
            (file_id, run_id, "b" * 64),
        )

    def create_staging_unit(
        self,
        unit_id: str = "stage-gen-1-1",
        *,
        run_id: str = "run-1",
        file_id: str = "file-gen",
        unit_label: str = "1",
        marker_order: int = 1,
        text: str = "Synthetic staged verse wording.",
        content_state: str = "text",
        footnotes: str | None = None,
        validation_status: str = "valid",
    ) -> None:
        self.db.execute(
            """
            INSERT INTO scripture_import_staging_units (
              id, import_run_id, source_file_id, versification_scheme_id,
              work_id, source_chapter_label, source_chapter_order,
              source_unit_label, source_unit_order, source_marker_order,
              unit_kind, content_state, text, footnote_metadata_json,
              structured_content_json, validation_status, created_at, updated_at
            ) VALUES (
              ?, ?, ?, 'scheme-import',
              'work-gen', '1', 1, ?, ?, ?,
              'verse', ?, ?, ?, '{"nodes":[]}', ?, 1000, 1000
            )
            """,
            (
                unit_id,
                run_id,
                file_id,
                unit_label,
                int(unit_label) if unit_label.isdigit() else marker_order,
                marker_order,
                content_state,
                text,
                footnotes,
                validation_status,
            ),
        )

    def transition(self, run_id: str, status: str, **extra: object) -> None:
        assignments = ["status = ?", "updated_at = updated_at + 1"]
        values: list[object] = [status]
        for key, value in extra.items():
            assignments.append(f"{key} = ?")
            values.append(value)
        values.append(run_id)
        self.db.execute(
            f"UPDATE scripture_import_runs SET {', '.join(assignments)} WHERE id = ?",
            values,
        )

    def create_validation_failure(self, run_id: str = "run-1") -> None:
        self.db.execute(
            """
            INSERT INTO scripture_import_validation_results (
              id, import_run_id, rule_code, severity, result,
              detail_json, created_at
            ) VALUES (?, ?, 'no-blocking-errors', 'blocking', 'failed',
                      '{"count":1}', 1000)
            """,
            ("validation-" + run_id, run_id),
        )

    def test_run_starts_acquired_and_records_creation_event(self) -> None:
        self.create_run()
        row = self.db.execute(
            "SELECT status FROM scripture_import_runs WHERE id = 'run-1'"
        ).fetchone()
        event = self.db.execute(
            """
            SELECT event_type, from_status, to_status, event_order
            FROM scripture_import_run_events WHERE import_run_id = 'run-1'
            """
        ).fetchone()
        self.assertEqual(row, ("acquired",))
        self.assertEqual(event, ("run_created", None, "acquired", 1))

    def test_invalid_state_transition_is_rejected(self) -> None:
        self.create_run()
        with self.assertRaises(sqlite3.IntegrityError):
            self.transition("run-1", "parsed")

    def test_valid_state_machine_and_approval_requirements(self) -> None:
        self.create_run()
        self.create_file()
        self.db.execute(
            """
            UPDATE scripture_import_files
            SET parse_status = 'parsed',
                canonical_usx_object_key = 'canonical-usx/run-1/GEN.usx',
                canonical_usx_sha256 = ?
            WHERE id = 'file-gen'
            """,
            ("c" * 64,),
        )
        self.create_staging_unit()
        for status in ("inventoried", "parsed", "validated"):
            self.transition("run-1", status)
        with self.assertRaises(sqlite3.IntegrityError):
            self.transition("run-1", "reviewed")
        self.transition(
            "run-1",
            "reviewed",
            approved_by="editor-1",
            approved_at=2000,
            approval_reference="review-record-1",
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.transition("run-1", "published")
        self.transition("run-1", "published", published_at=3000)
        self.assertEqual(
            self.db.execute(
                "SELECT status FROM scripture_import_runs WHERE id = 'run-1'"
            ).fetchone(),
            ("published",),
        )

    def test_published_run_requires_parsed_files_and_valid_staging_units(self) -> None:
        self.create_run()
        self.create_file()
        self.create_staging_unit(validation_status="pending")
        for status in ("inventoried", "parsed", "validated"):
            self.transition("run-1", status)
        self.transition("run-1", "reviewed", approved_by="editor", approved_at=2000)
        with self.assertRaises(sqlite3.IntegrityError):
            self.transition("run-1", "published", published_at=3000)

    def test_blocking_validation_failure_prevents_publication(self) -> None:
        self.create_run()
        self.create_file()
        self.create_staging_unit()
        self.create_validation_failure()
        for status in ("inventoried", "parsed", "validated"):
            self.transition("run-1", status)
        self.transition("run-1", "reviewed", approved_by="editor", approved_at=2000)
        with self.assertRaises(sqlite3.IntegrityError):
            self.transition("run-1", "published", published_at=3000)

    def test_source_archive_and_parser_provenance_is_immutable(self) -> None:
        self.create_run()
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "UPDATE scripture_import_runs SET source_archive_sha256 = ? WHERE id = 'run-1'",
                ("d" * 64,),
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "UPDATE scripture_import_runs SET parser_version = '0.4.11' WHERE id = 'run-1'"
            )

    def test_identical_archive_and_parser_run_is_unique(self) -> None:
        self.create_run()
        with self.assertRaises(sqlite3.IntegrityError):
            self.create_run(run_id="run-duplicate")

    def test_parsed_file_requires_canonical_usx_pointer_and_hash(self) -> None:
        self.create_run()
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                """
                INSERT INTO scripture_import_files (
                  id, import_run_id, member_name, member_sha256,
                  member_size_bytes, parse_status, created_at, updated_at
                ) VALUES ('bad-file', 'run-1', '02-GEN.usfm', ?, 50,
                          'parsed', 1000, 1000)
                """,
                ("b" * 64,),
            )

    def test_annotation_only_staging_unit_is_preserved(self) -> None:
        self.create_run()
        self.create_file()
        self.create_staging_unit(
            unit_id="stage-note",
            unit_label="2",
            marker_order=2,
            text="",
            content_state="annotation_only",
            footnotes='{"footnotes":[{"marker":"f"}]}',
        )
        state = self.db.execute(
            "SELECT content_state, text, footnote_metadata_json "
            "FROM scripture_import_staging_units WHERE id = 'stage-note'"
        ).fetchone()
        self.assertEqual(state[0:2], ("annotation_only", ""))
        self.assertIsNotNone(state[2])

    def test_invalid_annotation_only_staging_unit_is_rejected(self) -> None:
        self.create_run()
        self.create_file()
        with self.assertRaises(sqlite3.IntegrityError):
            self.create_staging_unit(
                unit_id="bad-note",
                unit_label="2",
                marker_order=2,
                text="",
                content_state="annotation_only",
            )

    def test_duplicate_source_reference_in_one_run_is_rejected(self) -> None:
        self.create_run()
        self.create_file()
        self.create_staging_unit()
        with self.assertRaises(sqlite3.IntegrityError):
            self.create_staging_unit(
                unit_id="duplicate-ref",
                marker_order=2,
                text="Another synthetic wording.",
            )

    def test_validation_evidence_is_append_only(self) -> None:
        self.create_run()
        self.db.execute(
            """
            INSERT INTO scripture_import_validation_results (
              id, import_run_id, rule_code, severity, result, created_at
            ) VALUES ('validation-1', 'run-1', 'zip-crc', 'info', 'passed', 1000)
            """
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "UPDATE scripture_import_validation_results SET result = 'failed' WHERE id = 'validation-1'"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "DELETE FROM scripture_import_validation_results WHERE id = 'validation-1'"
            )

    def test_edition_cannot_be_available_without_published_import(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "UPDATE translation_editions SET status = 'available' WHERE id = 'edition-import'"
            )

    def test_published_run_and_staging_are_immutable(self) -> None:
        self.create_run()
        self.create_file()
        self.db.execute(
            """
            UPDATE scripture_import_files
            SET parse_status = 'parsed',
                canonical_usx_object_key = 'canonical-usx/run-1/GEN.usx',
                canonical_usx_sha256 = ?
            WHERE id = 'file-gen'
            """,
            ("c" * 64,),
        )
        self.create_staging_unit()
        for status in ("inventoried", "parsed", "validated"):
            self.transition("run-1", status)
        self.transition("run-1", "reviewed", approved_by="editor", approved_at=2000)
        self.transition("run-1", "published", published_at=3000)
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "UPDATE scripture_import_staging_units SET text = 'changed' WHERE id = 'stage-gen-1-1'"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO scripture_import_staging_units (id, import_run_id, source_file_id, versification_scheme_id, work_id, source_chapter_label, source_chapter_order, source_unit_label, source_unit_order, source_marker_order, unit_kind, content_state, text, validation_status, created_at, updated_at) VALUES ('later', 'run-1', 'file-gen', 'scheme-import', 'work-gen', '1', 1, '2', 2, 2, 'verse', 'text', 'late', 'valid', 1000, 1000)"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.transition("run-1", "failed", failure_code="late-change")

    def test_run_events_are_append_only(self) -> None:
        self.create_run()
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "UPDATE scripture_import_run_events SET event_type = 'changed' WHERE import_run_id = 'run-1'"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "DELETE FROM scripture_import_run_events WHERE import_run_id = 'run-1'"
            )

    def test_foreign_key_integrity_is_preserved(self) -> None:
        self.create_run()
        self.create_file()
        self.create_staging_unit()
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])


if __name__ == "__main__":
    unittest.main()
