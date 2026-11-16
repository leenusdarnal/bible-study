# 4. Data Model

## 4.1 Design principles

- Use stable, non-positional identifiers (UUIDs or stable prefixed IDs) for important records.
- Do not use database row order or verse number alone as a universal identity.
- Separate canonical Scripture identity from translation-specific text.
- Preserve source provenance, licensing and review state.
- Represent uncertainty and disagreement explicitly.
- Keep personal user data separate from public knowledge.

## 4.2 Scripture model

Recommended logical entities:
- `canons`
- `books`
- `chapters`
- `verses`
- `translations`
- `verse_texts`
- `versification_schemes`
- `verse_mappings`

A common internal Scripture reference system should identify passages independently of translation text. A translation-specific record stores the actual verse text and edition metadata. Explicit mapping records handle differences in numbering, grouping and versification.

Do not assume every translation has a one-to-one verse mapping.

## 4.3 Entity model

Use a hybrid model:
- Central `entities` registry for common identity, names, aliases and metadata.
- Specialised records for `people`, `places`, `events`, `groups`, `objects`, themes and other entity types.
- Source-specific identifiers and aliases to reconcile imported datasets.
- Typed `relationships` between entities and passages.
- `relationship_evidence` records linking each relationship to its supporting sources and Scripture references.

Example: an explicit parent-child relationship and a thematic connection must use different relationship types and evidence classifications.

## 4.4 Cross-references and theology

Potential tables:
- `cross_references`
- `reference_types`
- `themes`
- `prophecies`
- `interpretations`
- `fulfilments`

Store relationship type, direction where relevant, source passages, supporting evidence and editorial status. Do not label a thematic association as an explicit quotation or fulfilment.

## 4.5 Geography and chronology

Potential tables:
- `locations`
- `location_identifications`
- `geometries`
- `chronology_models`
- `dated_events`
- `date_ranges`

Support ancient and modern place identifications, alternate identifications, geometries, source citations and confidence. Chronology records must retain model assumptions, date ranges and disputes; do not force one chronology.

D1 has no PostGIS. Use a compatible representation and application-level/geospatial strategy, and evaluate query requirements before choosing geometry storage.

## 4.6 Research and textual criticism

Potential tables:
- `research_articles`
- `claims`
- `manuscripts`
- `textual_variants`
- `sources`
- `source_versions`
- `citations`
- `licences`

Large permitted files and original source snapshots belong in R2; structured metadata and relationships belong in D1.

## 4.7 Editorial governance

Potential tables:
- `contributions`
- `reviews`
- `corrections`
- `audit_logs`

Keep review state, decision, reviewer, timestamps, reasons and revision history. Community submissions must not automatically become verified public facts.

## 4.8 User data

Potential tables:
- `users`
- `notes`
- `bookmarks`
- `highlights`
- `reading_progress`
- `user_preferences`
- `sessions` (depending on authentication implementation)

Personal notes and progress should reference stable Scripture IDs and remain private by default.

## 4.9 Suggested initial domain table map

| Domain | Main records |
|---|---|
| Scripture | canons, books, chapters, verses |
| Translations | translations, verse_texts, verse_mappings |
| Entities | entities, people, places, events, groups, objects |
| Relationships | relationships, relationship_evidence |
| Cross-references | cross_references, reference_types |
| Theology | themes, prophecies, interpretations, fulfilments |
| Geography | locations, location_identifications, geometries |
| Chronology | chronology_models, dated_events, date_ranges |
| Research | research_articles, claims, manuscripts, textual_variants |
| Sources | sources, citations, licences, source_versions |
| Editorial | contributions, reviews, corrections, audit_logs |
| Users | users, notes, bookmarks, highlights, reading_progress |

This is a logical starting model, not a frozen physical schema. Refine through migrations and tested use cases.
