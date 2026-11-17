# ADR-005: Relational Schema for Scripture and Research Data

- **Status:** Proposed; pending implementation proof and user approval of open implementation gates.
- **Date:** 2026-11-17
- **Related:** ADR-002, [Database Schema Proposal](../docs/11-database-schema.md), [ERDs](../docs/12-entity-relationship-diagrams.md).

## Context

The platform requires stable Bible references across translations and canons, a connected entity graph, research-grade citations, editorial history, private study data and a recoverable import pipeline. The initial database is Cloudflare D1, which uses SQLite semantics.

Printed book/chapter/verse numbers are not sufficient as permanent identity because editions can differ in versification. A single generic content table would also weaken referential integrity across Scripture, entities, evidence and user data.

## Decision

Adopt a domain-oriented relational schema:

1. Separate scriptural work identity, canon membership/order and versification. Use scriptural_works, canon_books, versification_schemes, scheme_chapters and scripture_units.
2. Attach translation text to units in the translation edition's own scheme. Use scripture_unit_mappings for one-to-one and non-one-to-one alignment.
3. Make passages first-class records with ordered segments, supporting continuous and non-contiguous references.
4. Use a central entity registry, specialised detail tables, typed relationships and evidence records.
5. Separate sources, source versions and exact citations. Connect atomic claims to citations and Scripture references through typed evidence relations.
6. Use revision-based publication and preserve review/audit history.
7. Isolate private user records and keep authentication secrets with the selected auth provider.
8. Preserve dataset versions, source snapshots, staging, external IDs and reversible entity merge history.
9. Use D1 for structured data and R2 for source files/media. Search projections are rebuildable; avoid PostgreSQL-specific and PostGIS assumptions.

## Consequences

**Benefits**
- Translation switching does not require re-keying personal annotations.
- Additional canons and versification systems can be added without redefining book identity.
- Verse mappings can express one-to-many and many-to-one differences.
- Research evidence, source versions and editorial decisions remain auditable.
- Knowledge-graph edges can distinguish explicit from thematic or inferred relationships.
- Public knowledge, editorial workflow and private user data have distinct lifecycle boundaries.

**Costs**
- The model is more complex than a table keyed by printed verse number.
- Passage resolution and translation alignment require tested application services.
- D1 cannot enforce every domain rule; services and integration tests must do so.
- The full proposal must be implemented incrementally, not in one migration.

## Implementation gates

Before production migrations:
- Select the initial versification scheme and OSIS/USX import profile.
- Verify the exact legal status and edition of the first complete translation corpus.
- Prove the authentication library with SvelteKit, Workers, D1 and Drizzle.
- Test migrations, constraints and foreign-key behaviour on D1.
- Validate non-one-to-one mappings using real source data.
- Confirm source/citation/licence fields against the first imported datasets.

## Rejected alternatives

- Printed verse numbers as primary keys: rejected because numbering differs and annotations would be fragile.
- One global verse table without scheme identity: rejected because it hides versification differences.
- All research/entities stored in JSON documents: rejected because joins, evidence traceability and integrity are core requirements.
- PostgreSQL/PostGIS now: rejected because Cloudflare-first D1 is the selected baseline and current requirements can be modelled without spatial extensions.
- Implementing every proposed table at launch: rejected in favour of migration slices and real-data validation.

## Review

Move this ADR to Accepted only after implementation gates are demonstrated with migrations and representative test data. If D1 materially prevents required integrity or query patterns, document measured evidence and propose a specific alternative before changing the platform decision.
