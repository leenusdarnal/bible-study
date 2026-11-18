# ADR-007: Dual Bible Text Corpus and Lossless USFM Import

- **Status:** Proposed — owner selection recorded; official archives acquired, structurally audited and all 149 USFM members semantically round-tripped; versification, publication and rights gates remain open.
- **Date:** 2026-11-17
- **Decision owner:** Bible Study Repo project owner.
- **Related:** [ADR-006: Scripture Core Schema](ADR-006-scripture-core-schema.md), [Source Selection](../docs/14-scripture-source-selection.md), [Dual Text Import Pipeline](../docs/15-dual-bible-text-import-pipeline.md).

## Context

The project requires complete English Bible text for the initial Scripture reader. The project owner selected both the World English Bible Update (WEBP) and the King James Version (KJV).

The official eBible.org USFM packages have been acquired and structurally audited. Their exact SHA-256 hashes, inventories and source-address differences are recorded in [Source Package Listing Review](../docs/23-source-package-listing-review.md). WEBP is presented as a public-domain 66-book protocanon edition. The KJV package is the 1769 standardised text and includes Apocrypha/Deuterocanon material. The eBible.org KJV notice identifies a UK Crown patent printing/import caveat, so the global publication scope needs a territorial rights review.

USFM can carry more than plain verse text: headings, paragraphs, poetry, footnotes, cross-references, alternate numbering and inline semantic markers. Versification differences can include one-to-many and many-to-one relationships, subverses, moved passages, absent references and colophons. A naive import that reduces each file to one plain-text row per verse would lose important structure.

## Decision

1. Include WEBP and KJV as two separate initial English translation editions.
2. Use the eBible.org USFM packages as the candidate import sources, subject to checksum, archive inventory, parsing and rights gates.
3. Preserve the original source archive, rights notice, source metadata, archive checksum, parser version and import-run manifest.
4. Parse each edition independently and maintain distinct source versification profiles until evidence supports a documented equivalence.
5. Preserve USFM structure in a loss-aware content representation. A flat verse-text field alone is not sufficient for the complete source.
6. Keep the initial reader scoped to the Protestant 66-book canon. Inventory all KJV source books, but do not silently discard or publish books outside that first-release canon.
7. Treat the STEPBible TVTMS data as a candidate crosswalk, not an unquestioned authority. Pin the inspected revision, provide requested attribution and review exceptional mappings.
8. Stage, validate, review and explicitly promote a complete import run. Failed runs must not partially modify published Scripture.

## Rationale

- WEBP provides a source-described public-domain 66-book edition suitable as a low-friction first corpus.
- KJV provides the requested historic English edition, but its source package and territorial caveat require separate rights handling.
- USFM gives both editions a common interchange format while retaining structural and editorial distinctions.
- Separate editions and versification profiles prevent translation wording and verse boundaries from being conflated.
- Immutable source artifacts and deterministic runs allow re-import, audit, parser correction and rollback.
- A reviewed crosswalk supports stable user references and future translation comparison without assuming all numbering traditions are identical.

## Consequences

### Positive

- Both selected English editions can be supported through one common, versioned import pipeline.
- Future translations can use the same source-manifest and parser architecture where they are supplied in compatible formats.
- User notes, bookmarks and highlights can attach to stable Scripture identities rather than a translation-specific verse string.
- Import history and source provenance remain auditable.

### Costs and constraints

- A structured content layer and richer mapping model are required before production import.
- The parser and mapping pipeline require real-file fixtures and manual review of exceptional cases.
- KJV distribution must be checked for each intended territory; the source notice does not resolve all jurisdictions.
- Source archives and parsed staging data require storage, backup and retention policies.
- The first public reader will not expose KJV books outside the Protestant 66-book canon unless a separate canon decision is made.

## Rejected alternatives

- **Import only WEBP:** rejected because the project owner selected both WEBP and KJV.
- **Use KJV as the universal verse-numbering authority without comparison:** rejected because source traditions and verse boundaries can differ.
- **Flatten USFM into plain verse strings only:** rejected because headings, poetry, footnotes, cross-references, alternate numbering and other structure would be lost.
- **Delete KJV Apocrypha/Deuterocanon files during ingestion:** rejected because it destroys source inventory and provenance. Canon membership belongs to publication scope, not source acquisition.
- **Automatically apply every TVTMS mapping:** rejected because mappings require source-profile identification and review of exceptional cases.

## Implementation gates

This ADR is not an approval to publish Bible text yet. Move it to Accepted only after:

- both source archives have been downloaded, checksummed and inventoried;
- WEBP and KJV source files pass USFM parser tests;
- loss-aware structured content and mapping storage are implemented and tested;
- the KJV rights review is documented for intended release territories;
- source-specific versification profiles and mapping exceptions are reviewed;
- publication and rollback tests pass.

No Bible text has yet been imported into D1 or published.
