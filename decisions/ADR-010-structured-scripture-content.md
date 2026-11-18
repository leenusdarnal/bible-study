# ADR-010: Structured Scripture Content Representation

- **Status:** Proposed; migration 0006 applies in fresh local D1 and the structured-node fixture passes CI run [44257329898](https://github.com/leenusdarnal/bible-study/actions/runs/44257329898)
- **Date:** 18 November 2026
- **Related:** ADR-006, ADR-007, ADR-009; [structured content model](../docs/26-structured-scripture-content-model.md); [import pipeline](../docs/15-dual-bible-text-import-pipeline.md).

## Context

The selected WEBP and KJV archives have passed structural ZIP validation and semantic USFM parsing/round-trip checks. The Scripture schema currently stores a plain-text translation projection and limited paragraph, poetry and footnote metadata. That is insufficient to represent the structured source content without loss.

## Decision proposal

Add a normalized, edition-specific content representation with two layers:

1. Ordered structural blocks, scoped to a book/chapter and optionally anchored to a source Scripture unit.
2. Ordered nested content nodes for text, inline spans, footnotes, cross-references, milestones, unknown markers, attributes and breaks.

Keep `translation_texts.text` as a plain-text projection for basic search and fallback rendering. It is not the lossless representation. Original archive bytes remain immutable and are retained separately.

Migration 0006 is a draft implementation of this model. It adds composite foreign keys, JSON validity checks, deterministic node ordering and same-block parent constraints.

## Consequences

- Reader rendering must consume the structured blocks/nodes to preserve headings, paragraphs, poetry, notes and inline semantics.
- Search indexing must use an explicit projection policy; note and cross-reference text should not be mixed into verse wording by default.
- Marker-to-node mappings require a versioned registry and representative visual review.
- The migration must be validated in SQLite and local D1 before it is considered implementation-ready.
- No production database has been modified and no Scripture text has been published by this decision.

## Acceptance criteria

- All migrations apply to a fresh local D1 database.
- Regression tests verify nested ordering, same-block parent integrity, JSON validation and book-level blocks.
- Representative WEBP/KJV content is rendered against the original source structure.
- Every source marker is either mapped to a known node or retained as an explicit unknown node with a review record.
- The importer produces a deterministic structured tree and plain-text projection from the same parser output.

## Open items

- [x] Complete D1 CI validation of migration 0006 and its structured-node fixture.
- Define the full source-marker registry from the audited archives.
- Build the deterministic source-to-staging importer.
- Review renderer fidelity for headings, poetry, notes and cross-references.
