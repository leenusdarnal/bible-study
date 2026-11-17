# 4. Data Model

## 4.1 Design principles

- Use stable, non-positional identifiers (UUIDs or stable prefixed IDs) for important records.
- Do not use database row order or printed verse number alone as a universal identity.
- Separate scriptural work identity, canon membership, versification and translation-specific text.
- Preserve source provenance, licensing and review state.
- Represent uncertainty and disagreement explicitly.
- Keep personal user data separate from public knowledge.
- Design for Cloudflare D1/SQLite semantics; do not assume PostgreSQL extensions or PostGIS.

## 4.2 Scripture model

The physical design separates:
- Scriptural works (the identity of a biblical book).
- Canons and canon-book membership/order.
- Versification schemes, chapters and Scripture units.
- Translation editions and translation-specific text.
- Explicit unit mappings between versification schemes.
- Passage references made of one or more ordered segments.

This model supports different canons, numbering systems and non-one-to-one verse mappings. Notes and highlights attach to stable passage identities rather than a translation's displayed verse number.

## 4.3 Entity model

Use a hybrid model:
- Central entities registry for common identity, names, aliases and metadata.
- Specialised detail tables for people, places, events, groups, objects and themes.
- Source-specific identifiers and aliases to reconcile imported datasets.
- Typed entity relationships.
- Relationship evidence linking graph edges to Scripture passages, claims and citations.

An explicit parent-child relationship and a thematic connection must use different relationship types and evidence classifications.

## 4.4 Cross-references and theology

Cross-references and theological connections should be typed, directional where appropriate, supported by source passages and evidence, and editorially reviewed. Do not label a thematic association as an explicit quotation or fulfilment. Dedicated prophecy, fulfilment and interpretation structures can be added as the use cases are implemented.

## 4.5 Geography and chronology

Support ancient and modern place identifications, alternate identifications, coordinates/geometries, source citations and confidence. Chronology records retain model assumptions, date ranges and disputes; do not force one chronology.

D1 has no PostGIS. Use compatible coordinate/geometry representations and an application-level strategy. Large or versioned GeoJSON may be stored in R2.

## 4.6 Research and textual criticism

Separate bibliographic sources, source versions and exact citations. Atomic claims connect to citations and Scripture passages through evidence relations such as supports, challenges, contextualises and mentions. Manuscripts, textual variants and variant readings should preserve the source and manuscript provenance.

Large permitted files and original source snapshots belong in R2; structured metadata and relationships belong in D1.

## 4.7 Editorial governance

Keep review state, decision, reviewer, timestamps, reasons and revision history. Community submissions must not automatically become verified public facts. Published content points to an approved revision; edits create a new revision rather than silently changing published history.

## 4.8 User data

Authentication-provider tables are selected only after a compatibility proof of concept. Application tables hold user profiles, roles, preferences, notes, bookmarks, highlights, reading plans and progress. Personal records are private by default and reference stable passage identities. Enforce ownership on the server.

## 4.9 Detailed physical design

The detailed table catalogue, key columns, integrity rules, index plan and migration slices are maintained in [11. Database Schema Proposal](11-database-schema.md). The domain relationships are illustrated in [12. Entity Relationship Diagrams](12-entity-relationship-diagrams.md).

The detailed schema is a proposed physical design, not a frozen migration. Validate it against real datasets and the deployed D1/SQLite runtime before production migrations.
