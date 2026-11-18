# ADR-006: Scripture Core Physical Schema

- **Status:** Proposed; draft migrations 0001–0004 apply in fresh local D1 CI, including grouped mapping tests; D1 preview and Drizzle reconciliation remain open.
- **Date:** 2026-11-17
- **Related:** ADR-005, [Scripture Core SQL Specification](../docs/13-scripture-core-implementation-spec.md).

## Context

The Scripture identity model is the foundation for Bible reading, translation switching, study notes, cross-references and research. It must preserve stable identities while supporting different canons and verse numbering.

## Decision

Prepare a first SQLite-compatible schema slice with:
- scriptural works, canons and canon-book order;
- versification schemes, chapters and scripture units;
- mapping groups with ordered source/target unit membership and optional pairwise edges;
- translation editions and text;
- passage references and ordered segments.

Use composite foreign keys where they enforce that units, translation text and passage segments belong to the correct scheme/work. Seed only the 66 book identities and order. Do not insert assumed verse counts or translation text until a source and versification scheme are verified.

## Consequences

- Referential integrity can catch several classes of cross-scheme and cross-book errors in the database itself.
- Passage ranges remain stable and can span chapters within a book.
- More complex import mapping and domain validation still require application-level services and tests.
- The SQL remains a draft until D1 behavioural edge cases are tested and the schema is reconciled with Drizzle-generated migrations. GitHub Actions applies migrations 0001–0004 to a fresh Wrangler local D1 database, seeds 66 Protestant books, verifies foreign-key integrity and tests a three-to-two mapping group (see run 44250525247).

## Review gates

- Validate schema and seed against SQLite and D1.
- Verify foreign-key checks, mapping-group membership and expected rejection cases.
- Select and document the initial versification source/version.
- Reconcile the DDL with the Drizzle schema before production use.
