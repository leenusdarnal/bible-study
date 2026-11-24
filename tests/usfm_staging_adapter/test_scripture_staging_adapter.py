from __future__ import annotations

import sqlite3
import unittest

from scripture_staging_adapter import StagingError, SyntheticStagingAdapter


def units(value="SYNTHETIC_FIXTURE_ALPHA"):
    return [{"unit_key": "fixture:alpha", "fixture_value": value}]


class SyntheticStagingAdapterTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.adapter = SyntheticStagingAdapter(self.db)

    def tearDown(self):
        self.db.close()

    def test_atomic_rollback_on_mid_batch_failure(self):
        with self.assertRaises(StagingError):
            self.adapter.stage("synthetic-run-a", "synthetic:source-a", [
                *units(), {"unit_key": "fixture:beta", "fixture_value": "SYNTHETIC_FIXTURE_BETA"}
            ], fail_after=1)
        self.assertEqual(self.db.execute("SELECT count(*) FROM synthetic_runs").fetchone()[0], 0)
        self.assertEqual(self.db.execute("SELECT count(*) FROM synthetic_units").fetchone()[0], 0)

    def test_identical_replay_is_idempotent(self):
        first = self.adapter.stage("synthetic-run-b", "synthetic:source-b", units())
        second = self.adapter.stage("synthetic-run-b", "synthetic:source-b", units())
        self.assertEqual(first["status"], "staged")
        self.assertEqual(second["status"], "already_staged")
        self.assertEqual(self.db.execute("SELECT count(*) FROM synthetic_units").fetchone()[0], 1)

    def test_changed_replay_is_rejected_without_mutation(self):
        self.adapter.stage("synthetic-run-c", "synthetic:source-c", units())
        with self.assertRaisesRegex(StagingError, "Idempotency conflict"):
            self.adapter.stage("synthetic-run-c", "synthetic:source-c", units("SYNTHETIC_FIXTURE_CHANGED"))
        self.assertEqual(self.db.execute("SELECT count(*) FROM synthetic_units").fetchone()[0], 1)

    def test_non_synthetic_inputs_are_rejected(self):
        with self.assertRaises(StagingError):
            self.adapter.stage("run-real", "source:real", units())
        with self.assertRaises(StagingError):
            self.adapter.stage("synthetic-run-d", "synthetic:source-d", [
                {"unit_key": "fixture:alpha", "fixture_value": "real scripture text"}
            ])
        self.assertEqual(self.db.execute("SELECT count(*) FROM synthetic_runs").fetchone()[0], 0)

    def test_duplicate_keys_and_extra_fields_are_rejected(self):
        with self.assertRaises(StagingError):
            self.adapter.stage("synthetic-run-e", "synthetic:source-e", [
                *units(), *units()
            ])
        with self.assertRaises(StagingError):
            self.adapter.stage("synthetic-run-f", "synthetic:source-f", [
                {"unit_key": "fixture:x", "fixture_value": "SYNTHETIC_FIXTURE_X", "text": "no"}
            ])

    def test_rollback_removes_only_selected_run(self):
        self.adapter.stage("synthetic-run-g", "synthetic:source-g", units())
        self.adapter.stage("synthetic-run-h", "synthetic:source-h", [
            {"unit_key": "fixture:beta", "fixture_value": "SYNTHETIC_FIXTURE_BETA"}
        ])
        self.adapter.rollback("synthetic-run-g")
        self.assertEqual(self.db.execute("SELECT run_id FROM synthetic_runs").fetchall(), [("synthetic-run-h",)])
        self.assertEqual(self.db.execute("SELECT run_id FROM synthetic_units").fetchall(), [("synthetic-run-h",)])


if __name__ == "__main__":
    unittest.main()
