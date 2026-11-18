# ADR-009: Dual-Edition Scripture Import Implementation

- **Status:** Proposed; source packages acquired, structurally audited and all 149 USFM members parsed/round-tripped; mapping approval and legal gates remain open.
- **Date:** 2026-11-17
- **Related:** ADR-005, ADR-006, [Source selection](../docs/14-scripture-source-selection.md), [Dual-text import pipeline](../docs/15-dual-bible-text-import-pipeline.md).

## Context

The project owner selected both WEBP and KJV for the initial English Bible text corpus. The editions were acquired from eBible.org in USFM and structurally audited. They differ in scope and verse addresses, and require semantic parsing, reviewed versification mappings and separate rights checks. KJV source package includes Apocrypha/Deuterocanon, while the first public release is scoped to the Protestant 66-book canon.

## Decision

Design the import as two independent translation editions sharing a common USFM parser:

- WEBP: eBible.org World English Bible Update, 66-book protocanon edition.
- KJV: eBible.org King James Version, 1769 standardised text, with the supplied Apocrypha/Deuterocanon inventory retained in source/staging records and only the Protestant 66-book subset in the initial public release.

For each edition, preserve an immutable source archive, checksum, source metadata, rights notice snapshot, parser version, source-specific versification profile and import run. Parse into staging, validate, review, then publish atomically.

Do not assume identical verse boundaries. Do not choose a canonical versification until the actual corpora are parsed and compared. Use STEPBible TVTMS as a candidate crosswalk with attribution and provenance, not as an unquestioned source of truth. The mapping layer must support split, merged, moved, absent and subverse relationships.

## Rights and distribution gate

WEBP's source notice states that the text is public domain and permits copying and redistribution, while requiring changed text not to be presented as the unchanged World English Bible. KJV's source notice describes the text as public domain outside the UK and notes UK Crown patent restrictions for printing/importing printed copies. The platform must obtain appropriate jurisdiction-specific review before global KJV distribution; this ADR is not a legal opinion.

## Consequences

- Both editions can be imported through one maintainable parser while preserving their independent source metadata.
- A 66-book public canon can coexist with a source package that contains additional books.
- The import pipeline must preserve semantic USFM markup and cannot flatten all content into verse strings.
- Canonical versification remains open until actual archive comparison and review.
- The project can reproduce and audit every published text edition from its source archive and import manifest.

## Review gates

- Acquire and checksum both source archives.
- Verify actual archive contents and book inventory.
- Parse both editions and pass structural/content integrity tests.
- Complete versification comparison and mapping review.
- Complete territorial rights review for the KJV and intended public distribution.
- Approve the canonical reference profile and implementation migration only after the evidence is available.
