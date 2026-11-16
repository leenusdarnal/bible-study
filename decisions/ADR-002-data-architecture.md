# ADR-002: Scripture and Knowledge Data Architecture

- **Status:** Accepted as logical architecture; physical schema to be validated.
- **Date:** 2026-11-16

## Context

The platform must support multiple canons and translations, stable user annotations, entity connections, alternative chronologies and research provenance.

## Decision

Use one canonical internal Scripture identity model with translation-specific verse text and explicit versification mappings. Use a central entity registry with specialised entity tables and typed relationships. Store evidence and provenance for relationships and claims. Use D1 for structured records and R2 for files.

Use stable IDs and preserve source-specific identifiers. Model uncertainty, disputed identifications and competing chronology models explicitly.

## Consequences

- Notes and highlights can remain attached across translation changes.
- Imported datasets can be reconciled without discarding their original identifiers.
- Additional canons and translations can be added without replacing the identity model.
- D1 and SQLite constraints require careful schema design; large files remain outside D1.
