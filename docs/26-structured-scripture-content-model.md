# 26. Structured Scripture Content Model

- **Status:** Proposed schema extension; migration 0006 is draft and passed SQLite regression tests plus local Cloudflare D1 migration/node-fixture CI ([run 44257036764](https://github.com/leenusdarnal/bible-study/actions/runs/44257036764)).
- **Purpose:** Preserve USFM-derived structure in addition to the plain-text verse projection.
- **Related:** [Dual-edition import pipeline](15-dual-bible-text-import-pipeline.md), [Scripture core schema](13-scripture-core-implementation-spec.md), [source archive audit](23-source-package-listing-review.md).

## 26.1 Why a structured layer is required

The existing `translation_texts` table stores one text string per source unit, plus paragraph/poetry hints and footnote metadata. That is useful as a search/display projection, but it cannot by itself faithfully represent all content found in USFM: section headings, paragraph boundaries, poetry line groups, nested character styles, divine-name markers, footnotes, cross-references, milestones, and unknown markers.

The import must not flatten away information that the parser has already preserved. The original checksummed archive remains the immutable source; the structured content tree is the queryable application representation; `translation_texts.text` remains a convenient verse-level plain-text projection.

## 26.2 Proposed two-level representation

### Content blocks

A `translation_content_blocks` row represents an ordered structural block within an edition and book, optionally scoped to a chapter and/or anchored to a source scripture unit.

Supported block types in migration 0006:
- `book_intro`
- `chapter_heading`
- `section_heading`
- `paragraph`
- `poetry_line_group`
- `list`
- `colophon`
- `peripheral`
- `other`

Each block retains its source member, source order, source marker and optional JSON metadata. The foreign keys ensure the edition, versification scheme, work, chapter and verse anchor remain consistent.

### Nested content nodes

A `translation_content_nodes` row represents a node within a block. Parent-child relationships preserve nested inline markup and annotation structure. Node types include:
- `text`
- `span`
- `footnote`
- `cross_reference`
- `milestone`
- `unknown_marker`
- `attribute`
- `break`

The tree retains source marker, text content, raw value, JSON attributes, source order and a deterministic `node_order_path`. The order path is unique within a block and provides stable sibling/descendant ordering without relying on row insertion order. Parent references are constrained to the same block.

## 26.3 Rendering and indexing rules

1. Render structural blocks in source order; do not treat headings or notes as ordinary verse wording.
2. Render nested nodes recursively, interpreting only known marker semantics. Unknown markers remain retained and can be surfaced in a diagnostic/review view.
3. Use `translation_texts.text` as a plain-text verse projection for basic search and fallback rendering. It is not the lossless source of truth for markup.
4. Store footnotes and cross-references as nodes anchored at their original position. Their body is represented by child nodes; do not append it to the verse text.
5. Preserve `translation_texts.content_state` for text-bearing, annotation-only and explicit empty source markers.
6. Generate search text from an approved deterministic projection of the structured tree; exclude footnote bodies and cross-reference labels by default, while retaining separate indexes for notes and references.
7. Keep raw USFM archive bytes in immutable source storage; never regenerate the archive from the database representation.

## 26.4 Migration and validation

Migration `docs/sql/0006_structured_translation_content.sql` creates the block and node tables with:
- composite foreign keys tying content to the selected edition and source versification;
- optional chapter and verse anchors;
- JSON validity checks;
- a parent-node foreign key constrained to the same block;
- deterministic unique node order paths;
- indexes for location, anchor and node traversal.

Tests cover nested inline content, source marker retention, ordering, cross-block parent rejection, invalid JSON, duplicate paths and book-level introduction blocks. The local D1 workflow also applies migrations 0001–0006 and exercises a nested span/text node tree. The migration is a draft schema experiment, not a production deployment.

## 26.5 Known limitations and next gates

- The schema is a normalized content tree, not a complete implementation of every USFM/USX semantic convention.
- Marker-to-node mapping and exact handling of all markers in the two source archives still require a marker inventory and representative visual review.
- A deterministic importer must generate both the structured tree and plain-text projection from the same parser output.
- The app must support footnote/cross-reference navigation and paragraph/poetry layout before the import is considered display-ready.
- D1 production migration, import staging, deterministic re-run/idempotency, full corpus counts and reviewer sign-off remain pending.
