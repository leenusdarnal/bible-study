# ADR-006: Scripture Core Physical Schema

- **Status:** Proposed; SQL draft only, not yet applied to D1.
- **Date:** 2026-11-17
- **Related:** ADR-005, [Scripture Core SQL Specification](../docs/13-scripture-core-implementation-spec.md).

## Context

The Scripture identity model is the foundation for Bible reading, translation switching, study notes, cross-references and research. It must preserve stable identities while supporting different canons and verse numbering.

## Decision

Prepare a first SQLite-compatible schema slice with:
- scriptural works, canons and canon-book order;
- versification schemes, chapters and scripture units;
- unit mappings;
- translation editions and text;
- passage references and ordered segments.

Use composite foreign keys where they enforce that units, translation text and passage segments belong to the correct scheme/work. Seed only the 66 book identities and order. Do not insert assumed verse counts or translation text until a source and versification scheme are verified.

## Consequences

- Referential integrity can catch several classes of cross-scheme and cross-book errors in the database itself.
- Passage ranges remain stable and can span chapters within a book.
- More complex import mapping and domain validation still require application-level services and tests.
- The SQL is a draft until it is tested against local SQLite and Cloudflare D1 and reconciled with Drizzle-generated migrations.

## Review gates

- Validate schema and seed against SQLite and D1.
- Verify foreign-key checks and expected rejection cases.
- Select and document the initial versification source/version.
- Reconcile the DDL with the Drizzle schema before production use.
