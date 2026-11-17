# 13. Scripture Core SQL Implementation Specification

- **Status:** Draft SQL specification; not an applied migration.
- **Target:** Cloudflare D1 / SQLite.
- **Purpose:** Turn the logical Scripture model into testable DDL and initial canon seed data.
- **Related:** [Database schema](11-database-schema.md), [ERDs](12-entity-relationship-diagrams.md), [ADR-005](../decisions/ADR-005-database-schema.md).

## 13.1 Files in this directory

- `sql/0001_scripture_core.sql` — core Scripture and translation tables.
- `sql/0002_seed_protestant_66.sql` — 66-book identity and order seed only.

These are specifications in the documentation repository. They are not production migrations and must not be run against a live database without review, testing and transfer into the separate application repository.

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

Run these checks in a disposable SQLite database and then against a D1 local/preview database:

1. Apply the schema to an empty database.
2. Apply the 66-book seed; verify 66 books and positions 1–66.
3. Verify 39 Old Testament and 27 New Testament book records.
4. Insert a test scheme, one book's chapters and sample units.
5. Insert a translation edition and its text; verify a unit from another scheme is rejected.
6. Insert a passage spanning two chapters of the same book; verify it succeeds.
7. Attempt a passage whose start/end belong to different books; verify the composite foreign key rejects it.
8. Insert one-to-many and many-to-one mappings across schemes.
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

Use Wrangler's documented D1 migration workflow and keep migration files in the application repository once that repository exists. Review generated Drizzle migrations, especially table rebuilds and foreign-key handling. Do not assume that every generic SQLite migration sequence behaves identically under D1's migration execution.

## 13.5 Acceptance criteria

This slice is ready to be considered implementation-approved only when:
- DDL applies cleanly to a fresh D1 database.
- The 66-book seed is repeatable only through the migration history (not by blindly re-running inserts).
- All listed integrity tests pass.
- A real chosen versification import is mapped without forcing false one-to-one assumptions.
- The implementation's Drizzle schema and generated migrations match the SQL specification.
- The documentation and ERD are updated from the tested implementation.
