"""Regression tests for the draft SQLite reading-progress migration.

Run from the repository root:
    python -m unittest discover -s tests/sqlite -v

These tests exercise the documented SQL against SQLite. They are not a substitute
for running the same migrations against Cloudflare D1 local/preview.
"""
from pathlib import Path
import sqlite3
import unittest


ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = ROOT / "docs" / "sql"
NOW = 1_800_000_000_000


class ReadingProgressMigrationTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript((SQL_DIR / "0001_scripture_core.sql").read_text(encoding="utf-8"))
        self.db.executescript((SQL_DIR / "0002_seed_protestant_66.sql").read_text(encoding="utf-8"))

        self.db.execute(
            """INSERT INTO versification_schemes
               (id, code, name, description, version, source_note, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("scheme-test-a", "test-a", "Test scheme A", "Test-only scheme", "1", "Unit tests", "verified", NOW, NOW),
        )
        self.db.execute(
            """INSERT INTO versification_schemes
               (id, code, name, description, version, source_note, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("scheme-test-b", "test-b", "Test scheme B", "Second test-only scheme", "1", "Unit tests", "verified", NOW, NOW),
        )

        # A work in a second test canon proves that a tracker cannot point outside
        # its selected canon, even if that work has a valid chapter in the same scheme.
        self.db.execute(
            """INSERT INTO scriptural_works
               (id, usfm_code, osis_code, standard_name, testament, genre, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            ("work-tobit", "TOB", "Tob", "Tobit (test)", "old", None, NOW, NOW),
        )
        self.db.execute(
            """INSERT INTO canons
               (id, code, name, tradition_label, description, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            ("canon-test-other", "other-test", "Other test canon", "Test", "Test only", "active", NOW, NOW),
        )
        self.db.execute(
            """INSERT INTO canon_books
               (id, canon_id, work_id, position, display_name, is_included)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ("canonbook-test-tobit", "canon-test-other", "work-tobit", 1, "Tobit", 1),
        )

        self.db.executemany(
            """INSERT INTO scheme_chapters
               (id, scheme_id, work_id, chapter_label, chapter_order)
               VALUES (?, ?, ?, ?, ?)""",
            [
                ("gen-1-a", "scheme-test-a", "work-gen", "1", 1),
                ("gen-2-a", "scheme-test-a", "work-gen", "2", 2),
                ("exo-1-a", "scheme-test-a", "work-exo", "1", 1),
                ("tob-1-a", "scheme-test-a", "work-tobit", "1", 1),
                ("gen-1-b", "scheme-test-b", "work-gen", "1", 1),
            ],
        )

        self.db.executemany(
            """INSERT INTO scripture_units
               (id, scheme_id, work_id, chapter_id, unit_label, unit_order, unit_kind)
               VALUES (?, ?, 'work-gen', ?, ?, ?, 'verse')""",
            [
                ("a-v1", "scheme-test-a", "gen-1-a", "1", 1),
                ("a-v2", "scheme-test-a", "gen-1-a", "2", 2),
                ("a-v3", "scheme-test-a", "gen-1-a", "3", 3),
                ("b-v1", "scheme-test-b", "gen-1-b", "1", 1),
                ("b-v2", "scheme-test-b", "gen-1-b", "2", 2),
                ("b-v3", "scheme-test-b", "gen-1-b", "3", 3),
            ],
        )

        self.db.executescript((SQL_DIR / "0003_reading_progress.sql").read_text(encoding="utf-8"))
        # Seed a legacy pairwise mapping to prove migration 0004 preserves it.
        self.db.execute(
            """INSERT INTO scripture_unit_mappings
               (id, from_unit_id, from_scheme_id, to_unit_id, to_scheme_id,
                mapping_type, source_id, confidence, notes, review_status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("legacy-map", "a-v1", "scheme-test-a", "b-v1", "scheme-test-b",
             "equivalent", "test-source", "high", "legacy mapping fixture", "approved", NOW),
        )
        self.db.executescript((SQL_DIR / "0004_versification_mapping_groups.sql").read_text(encoding="utf-8"))

    def tearDown(self):
        self.db.close()

    def make_tracker(self, tracker_id, scope="all_books", canon="canon-protestant-66", scheme="scheme-test-a"):
        # The SQL requires a selected tracker to be assembled transactionally:
        # insert as all_books, add at least one selected book, then activate its scope.
        self.db.execute(
            """INSERT INTO reading_trackers
               (id, user_id, name, canon_id, versification_scheme_id, scope_mode, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, 'all_books', ?, ?)""",
            (tracker_id, "test-user", tracker_id, canon, scheme, NOW, NOW),
        )
        if scope == "selected_books":
            self.db.execute(
                """INSERT INTO reading_tracker_books
                   (id, tracker_id, canon_id, work_id, display_order)
                   VALUES (?, ?, ?, ?, ?)""",
                (f"{tracker_id}-book-1", tracker_id, canon, "work-gen", 1),
            )
            self.db.execute(
                "UPDATE reading_trackers SET scope_mode = 'selected_books', updated_at = ? WHERE id = ?",
                (NOW, tracker_id),
            )

    def add_progress(self, tracker_id, progress_id, work="work-gen", chapter="gen-1-a",
                     scheme="scheme-test-a", state="read", completed=NOW):
        self.db.execute(
            """INSERT INTO reading_tracker_chapter_progress
               (id, tracker_id, canon_id, versification_scheme_id, work_id, chapter_id,
                progress_state, started_at, completed_at, updated_at)
               VALUES (?, ?, 'canon-protestant-66', ?, ?, ?, ?, ?, ?, ?)""",
            (progress_id, tracker_id, scheme, work, chapter, state, NOW, completed, NOW),
        )

    def assert_integrity_error(self, sql, params=()):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(sql, params)


    def test_mapping_group_supports_three_to_two_unit_relationship(self):
        self.db.execute(
            """INSERT INTO scripture_mapping_groups
               (id, from_scheme_id, to_scheme_id, group_type, source_id, source_reference,
                confidence, review_status, rationale, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("group-3-to-2", "scheme-test-a", "scheme-test-b", "complex",
             "tvts-test", "Rom.14:24-26 <> Rom.16:25-27", "unreviewed", "pending",
             "Three source units correspond to two target units.", NOW, NOW),
        )
        members = [
            ("group-from-1", "group-3-to-2", "scheme-test-a", "scheme-test-b", "from", "scheme-test-a", "a-v1", 1),
            ("group-from-2", "group-3-to-2", "scheme-test-a", "scheme-test-b", "from", "scheme-test-a", "a-v2", 2),
            ("group-from-3", "group-3-to-2", "scheme-test-a", "scheme-test-b", "from", "scheme-test-a", "a-v3", 3),
            ("group-to-1", "group-3-to-2", "scheme-test-a", "scheme-test-b", "to", "scheme-test-b", "b-v1", 1),
            ("group-to-2", "group-3-to-2", "scheme-test-a", "scheme-test-b", "to", "scheme-test-b", "b-v2", 2),
        ]
        self.db.executemany(
            """INSERT INTO scripture_mapping_group_members
               (id, mapping_group_id, from_scheme_id, to_scheme_id, side, scheme_id, unit_id, member_order)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            members,
        )
        counts = dict(self.db.execute(
            """SELECT side, COUNT(*) FROM scripture_mapping_group_members
               WHERE mapping_group_id = ? GROUP BY side""",
            ("group-3-to-2",),
        ).fetchall())
        self.assertEqual(counts, {"from": 3, "to": 2})

        # A pairwise edge is valid only when both endpoints are members of this group.
        self.db.execute(
            """INSERT INTO scripture_unit_mappings
               (id, from_unit_id, from_scheme_id, to_unit_id, to_scheme_id, mapping_group_id,
                mapping_type, source_id, confidence, notes, review_status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("group-edge-1", "a-v1", "scheme-test-a", "b-v1", "scheme-test-b",
             "group-3-to-2", "partial", "tvts-test", "unreviewed", None, "pending", NOW),
        )
        self.assertEqual(
            self.db.execute(
                "SELECT COUNT(*) FROM scripture_unit_mappings WHERE mapping_group_id = ?",
                ("group-3-to-2",),
            ).fetchone()[0],
            1,
        )

    def test_mapping_group_rejects_member_from_wrong_side_scheme(self):
        self.db.execute(
            """INSERT INTO scripture_mapping_groups
               (id, from_scheme_id, to_scheme_id, group_type, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ("group-side-check", "scheme-test-a", "scheme-test-b", "moved", NOW, NOW),
        )
        self.assert_integrity_error(
            """INSERT INTO scripture_mapping_group_members
               (id, mapping_group_id, from_scheme_id, to_scheme_id, side, scheme_id, unit_id, member_order)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            ("bad-side-member", "group-side-check", "scheme-test-a", "scheme-test-b",
             "from", "scheme-test-b", "b-v1", 1),
        )

    def test_mapping_group_edge_rejects_non_member_endpoint(self):
        self.db.execute(
            """INSERT INTO scripture_mapping_groups
               (id, from_scheme_id, to_scheme_id, group_type, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ("group-edge-check", "scheme-test-a", "scheme-test-b", "split", NOW, NOW),
        )
        self.db.executemany(
            """INSERT INTO scripture_mapping_group_members
               (id, mapping_group_id, from_scheme_id, to_scheme_id, side, scheme_id, unit_id, member_order)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                ("edge-from-member", "group-edge-check", "scheme-test-a", "scheme-test-b", "from", "scheme-test-a", "a-v1", 1),
                ("edge-to-member", "group-edge-check", "scheme-test-a", "scheme-test-b", "to", "scheme-test-b", "b-v1", 1),
            ],
        )
        self.assert_integrity_error(
            """INSERT INTO scripture_unit_mappings
               (id, from_unit_id, from_scheme_id, to_unit_id, to_scheme_id, mapping_group_id,
                mapping_type, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            ("bad-edge", "a-v1", "scheme-test-a", "b-v3", "scheme-test-b",
             "group-edge-check", "partial", NOW),
        )

    def test_mapping_group_migration_preserves_existing_pairwise_rows(self):
        row = self.db.execute(
            """SELECT id, mapping_group_id, mapping_type, review_status
               FROM scripture_unit_mappings WHERE id = 'legacy-map'"""
        ).fetchone()
        self.assertEqual(row, ("legacy-map", None, "equivalent", "approved"))

    def test_all_books_tracker_accepts_chapters_in_its_canon(self):
        self.make_tracker("all-books")
        self.add_progress("all-books", "progress-genesis")
        self.add_progress("all-books", "progress-exodus", work="work-exo", chapter="exo-1-a")
        count = self.db.execute(
            "SELECT COUNT(*) FROM reading_tracker_chapter_progress WHERE tracker_id = ?",
            ("all-books",),
        ).fetchone()[0]
        self.assertEqual(count, 2)

    def test_selected_scope_rejects_new_progress_for_unselected_book(self):
        self.make_tracker("genesis-only", scope="selected_books")
        self.add_progress("genesis-only", "progress-genesis")
        self.assert_integrity_error(
            """INSERT INTO reading_tracker_chapter_progress
               (id, tracker_id, canon_id, versification_scheme_id, work_id, chapter_id,
                progress_state, started_at, completed_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("progress-exodus", "genesis-only", "canon-protestant-66", "scheme-test-a",
             "work-exo", "exo-1-a", "read", NOW, NOW, NOW),
        )

    def test_selected_scope_cannot_be_activated_without_a_book(self):
        self.make_tracker("empty-scope")
        self.assert_integrity_error(
            "UPDATE reading_trackers SET scope_mode = 'selected_books' WHERE id = ?",
            ("empty-scope",),
        )
        self.assertEqual(
            self.db.execute("SELECT scope_mode FROM reading_trackers WHERE id = ?", ("empty-scope",)).fetchone()[0],
            "all_books",
        )

    def test_selected_scope_cannot_be_created_directly_without_transactional_book_selection(self):
        self.assert_integrity_error(
            """INSERT INTO reading_trackers
               (id, user_id, name, canon_id, versification_scheme_id, scope_mode, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, 'selected_books', ?, ?)""",
            ("bad-selected", "test-user", "Empty", "canon-protestant-66", "scheme-test-a", NOW, NOW),
        )

    def test_selected_scope_cannot_delete_its_last_book(self):
        self.make_tracker("selected-delete", scope="selected_books")
        self.assert_integrity_error(
            "DELETE FROM reading_tracker_books WHERE tracker_id = ?",
            ("selected-delete",),
        )

    def test_selected_scope_cannot_move_its_last_book_to_another_tracker(self):
        self.make_tracker("selected-source", scope="selected_books")
        self.make_tracker("destination")
        self.assert_integrity_error(
            """UPDATE reading_tracker_books SET tracker_id = ?
               WHERE tracker_id = ? AND work_id = ?""",
            ("destination", "selected-source", "work-gen"),
        )

    def test_progress_cannot_be_edited_after_its_book_leaves_selected_scope(self):
        self.make_tracker("scope-edit", scope="selected_books")
        # Add a second selected book, record progress, then remove that book from the scope.
        self.db.execute(
            """INSERT INTO reading_tracker_books
               (id, tracker_id, canon_id, work_id, display_order)
               VALUES (?, ?, ?, ?, ?)""",
            ("scope-edit-exodus", "scope-edit", "canon-protestant-66", "work-exo", 2),
        )
        self.add_progress("scope-edit", "progress-exodus", work="work-exo", chapter="exo-1-a")
        self.db.execute(
            "DELETE FROM reading_tracker_books WHERE tracker_id = ? AND work_id = ?",
            ("scope-edit", "work-exo"),
        )
        self.assert_integrity_error(
            """UPDATE reading_tracker_chapter_progress
               SET progress_state = 'in_progress', completed_at = NULL, updated_at = ?
               WHERE id = ?""",
            (NOW + 1, "progress-exodus"),
        )

    def test_composite_foreign_key_rejects_another_versification_scheme(self):
        self.make_tracker("scheme-locked")
        self.assert_integrity_error(
            """INSERT INTO reading_tracker_chapter_progress
               (id, tracker_id, canon_id, versification_scheme_id, work_id, chapter_id,
                progress_state, started_at, completed_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("wrong-scheme", "scheme-locked", "canon-protestant-66", "scheme-test-b",
             "work-gen", "gen-1-b", "read", NOW, NOW, NOW),
        )

    def test_composite_foreign_key_rejects_a_work_outside_tracker_canon(self):
        self.make_tracker("canon-locked")
        self.assert_integrity_error(
            """INSERT INTO reading_tracker_chapter_progress
               (id, tracker_id, canon_id, versification_scheme_id, work_id, chapter_id,
                progress_state, started_at, completed_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("wrong-canon", "canon-locked", "canon-protestant-66", "scheme-test-a",
             "work-tobit", "tob-1-a", "read", NOW, NOW, NOW),
        )

    def test_two_trackers_can_store_independent_states_for_same_chapter(self):
        self.make_tracker("tracker-one")
        self.make_tracker("tracker-two")
        self.add_progress("tracker-one", "progress-one", state="read", completed=NOW)
        self.add_progress("tracker-two", "progress-two", state="in_progress", completed=None)
        states = dict(self.db.execute(
            "SELECT tracker_id, progress_state FROM reading_tracker_chapter_progress"
        ).fetchall())
        self.assertEqual(states, {"tracker-one": "read", "tracker-two": "in_progress"})

    def test_unique_and_timestamp_constraints_are_enforced(self):
        self.make_tracker("unique-check")
        self.add_progress("unique-check", "first")
        self.assert_integrity_error(
            """INSERT INTO reading_tracker_chapter_progress
               (id, tracker_id, canon_id, versification_scheme_id, work_id, chapter_id,
                progress_state, started_at, completed_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("duplicate", "unique-check", "canon-protestant-66", "scheme-test-a",
             "work-gen", "gen-1-a", "read", NOW, NOW, NOW),
        )
        self.assert_integrity_error(
            """INSERT INTO reading_tracker_chapter_progress
               (id, tracker_id, canon_id, versification_scheme_id, work_id, chapter_id,
                progress_state, started_at, completed_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("bad-state", "unique-check", "canon-protestant-66", "scheme-test-a",
             "work-gen", "gen-2-a", "read", NOW, None, NOW),
        )

    def test_tracker_delete_cascades_only_dependent_tracker_rows(self):
        self.make_tracker("cascade-check", scope="selected_books")
        self.add_progress("cascade-check", "cascade-progress")
        self.db.execute("DELETE FROM reading_trackers WHERE id = ?", ("cascade-check",))
        self.assertEqual(
            self.db.execute("SELECT COUNT(*) FROM reading_tracker_books WHERE tracker_id = ?", ("cascade-check",)).fetchone()[0],
            0,
        )
        self.assertEqual(
            self.db.execute("SELECT COUNT(*) FROM reading_tracker_chapter_progress WHERE tracker_id = ?", ("cascade-check",)).fetchone()[0],
            0,
        )

    def test_foreign_key_check_is_clean(self):
        self.make_tracker("fk-check", scope="selected_books")
        self.add_progress("fk-check", "fk-progress")
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])


if __name__ == "__main__":
    unittest.main()
