# 13. Scripture Core SQL Implementation Specification

- **Status:** Draft SQL specification; not an applied migration.
- **Target:** Cloudflare D1 / SQLite.
- **Purpose:** Turn the logical Scripture model into testable DDL and initial canon seed data.
- **Related:** [Database schema](11-database-schema.md), [ERDs](12-entity-relationship-diagrams.md), [ADR-005](../decisions/ADR-005-database-schema.md).

## 13.1 Files in this directory

- `sql/0001_scripture_core.sql` — core Scripture and translation tables.
- `sql/0002_seed_protestant_66.sql` — 66-book identity and order seed only.
- `sql/0003_reading_progress.sql` — draft account-owned tracker tables and integrity triggers.
- `sql/0004_versification_mapping_groups.sql` — grouped source/target unit sets and constrained pairwise mapping edges.
- `sql/0005_translation_text_content_states.sql` — explicit text-bearing, annotation-only and empty source-marker states.
- `tests/sqlite/test_reading_progress_migration.py` — standard-library SQLite regression tests for the draft tracker migration.
- `tests/sqlite/test_translation_text_content_state_migration.py` — standard-library SQLite tests for source text/annotation state integrity.

These are specifications in the documentation repository. They are not production migrations and must not be run against a live database without review, testing and transfer into the separate application repository. Migration 0003 requires migration 0001, the canon seed and selected canon/scheme records. Migration 0004 requires migration 0001 and preserves existing pairwise mappings while adding explicit mapping groups. Migration 0005 requires migration 0001 and enforces consistent translation text states when a source unit contains text, only annotations, or an explicitly empty marker.

## 13.2 What migration 0001 creates

- Scriptural work identities.
- Canons and canon-book ordering.
- Versification schemes, chapters and Scripture units.
- Explicit mappings between Scripture units.
- Translation editions and text records.
- Passage references and ordered segments.
- Foreign keys and lookup indexes.

The schema uses composite foreign keys to ensure:
- A Scripture unit belongs to its declared chapter, work and scheme.
- A translation text uses a unit from its edition's own versification scheme.
- A passage segment's start and end units belong to the passage's declared scheme and the same scriptural work.

The segment endpoints can span chapters within one book. A reference that crosses books should be represented as multiple segments.

## 13.3 What the seed does not do

The seed inserts the 66 book identities and Protestant book order, retaining separate USFM identifiers and OSIS identifiers. It deliberately does **not** invent or insert chapter counts, verse counts, versification details or Bible text. Those must come from a verified import source and a selected versification profile.

The initial versification scheme remains an open decision. A scheme record should only be seeded after its source, version and numbering rules are selected and documented.

## 13.4 Validation plan

Run these checks in a disposable SQLite database and against D1 local. The repository CI now applies migrations 0001–0005 to a fresh local D1 database, seeds the Protestant 66-book canon, asserts the book count and foreign-key integrity, and tests grouped mappings, reading-progress integrity and translation text content states. D1 preview/remote behavioural validation remains a separate pre-production gate:

1. Apply the schema to an empty database.
2. Apply the 66-book seed; verify 66 books and positions 1–66.
3. Verify 39 Old Testament and 27 New Testament book records.
4. Insert a test scheme, one book's chapters and sample units.
5. Insert a translation edition and its text; verify a unit from another scheme is rejected.
6. Insert a passage spanning two chapters of the same book; verify it succeeds.
7. Attempt a passage whose start/end belong to different books; verify the composite foreign key rejects it.
8. Insert one-to-many, many-to-one and many-to-many mapping groups; verify group-side membership and optional pairwise edge constraints.
9. Attempt to delete a referenced published unit; verify RESTRICT prevents it.
10. Run `PRAGMA foreign_key_check;` and verify it returns no rows.

### Useful local SQLite checks

```sql
SELECT COUNT(*) AS book_count FROM canon_books
WHERE canon_id = 'canon-protestant-66';

SELECT sw.testament, COUNT(*) AS book_count
FROM canon_books cb
JOIN scriptural_works sw ON sw.id = cb.work_id
WHERE cb.canon_id = 'canon-protestant-66'
GROUP BY sw.testament;

PRAGMA foreign_key_check;
```

### D1 migration handling

Use Wrangler's documented D1 migration workflow and keep migration files in the application repository once that repository exists. D1 enforces foreign keys by default. Cloudflare documents `PRAGMA defer_foreign_keys = on` for migrations that temporarily need to violate constraints within a transaction; unresolved violations still fail at transaction end. Do not use `PRAGMA defer_foreign_keys = off` as a validation step. Run `PRAGMA foreign_key_check` to inspect violations. Review generated Drizzle migrations, especially table rebuilds and foreign-key handling. If using Drizzle's nested migration layout, configure Wrangler's `migrations_pattern` to match the generated files. Do not assume every generic SQLite migration sequence behaves identically under D1.

## 13.5 Versification mapping groups migration 0004

Migration 0004 adds mapping groups and ordered group members so one-to-many, many-to-one, moved, subverse, absent and complex mappings can be represented explicitly. It preserves pre-existing pairwise mappings as ungrouped rows and requires optional pairwise edges to use units already registered as members of the referenced group.

## 13.6 Reading progress migration 0003

Migration 0003 adds account-owned trackers with explicit canon, scheme and scope, selected-book membership, chapter progress, indexes and triggers that reject progress outside selected-book scope, re-check edits to historic out-of-scope progress, require at least one selected book before activating selected scope, and prevent removing or moving the final selected book. Selected scope is created transactionally by inserting a tracker as all-books, adding selected-book rows, then switching its scope before commit. Guest progress remains in IndexedDB. The auth-provider user foreign key is deferred until the authentication provider is selected; server-side ownership validation remains mandatory.

Validate 0003 only after the Scripture core, canon seed and selected versification data are present. Test all-books and selected-books trackers, cross-scheme rejection, cross-canon rejection, duplicate chapter rows, state/timestamp checks, selected-scope changes, cascade behaviour and PRAGMA foreign_key_check. Guest migration is a service-level workflow and is not implemented by this SQL file.

Run the repository's SQLite regression tests with `python -m unittest discover -s tests/sqlite -v`. These tests target SQLite. A separate GitHub Actions job also applies all four migrations to Wrangler local D1 and checks the 66-book seed plus foreign-key integrity. Local D1 trigger tests now cover selected-scope activation and the key rejection cases; D1 preview/remote validation and production safety review remain outstanding.

## 13.7 Acceptance criteria

This slice is ready to be considered implementation-approved only when:
- [x] DDL migrations 0001–0004 apply cleanly to a fresh Wrangler local D1 database; grouped three-to-two mapping storage is exercised in CI run 44250525247.
- The 66-book seed is repeatable only through the migration history (not by blindly re-running inserts).
- All listed integrity tests pass.
- A real chosen versification import is mapped without forcing false one-to-one assumptions.
- The implementation's Drizzle schema and generated migrations match the SQL specification.
- The documentation and ERD are updated from the tested implementation.


## 13.8 Current implementation references

- [Cloudflare D1 foreign keys](https://developers.cloudflare.com/d1/sql-api/foreign-keys/) — enforcement defaults and deferred validation.
- [Cloudflare D1 migrations](https://developers.cloudflare.com/d1/reference/migrations/) — migration files, Wrangler configuration and migration patterns.
- [Drizzle ORM with Cloudflare D1](https://orm.drizzle.team/docs/sqlite/connect-cloudflare-d1) — D1 driver and Workers integration.
