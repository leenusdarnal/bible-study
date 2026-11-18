# 29. USFM Marker Interpretation Registry

- **Status:** Initial partial registry implemented; every mapping remains pending editorial review.
- **Registry:** `data/usfm/marker-registry.json`
- **Validator:** `tools/validate_usfm_marker_registry.py`
- **Tests:** `tests/usfm_registry/`
- **Related:** [Source archive audit](24-source-archive-audit-tool.md), [Structured Scripture content model](26-structured-scripture-content-model.md), [Import staging and publication](27-scripture-import-staging-and-publication.md).

## 29.1 Purpose and evidence boundary

The registry provides a versioned, machine-readable bridge from USFM/USX marker styles to the structured content model. The official WEBP and KJV archives were parsed and canonical-XML round-tripped with USFMTC 0.4.10 for all 149 members. The source files do not declare a USFM version; the parser's successful 2.5 profile is a compatibility result, not a publisher declaration.

The registry is intentionally labelled **initial partial**. It contains common structural, paragraph, poetry, heading, annotation and character styles as conservative implementation hypotheses. It is not a generated inventory of every style actually present in both archives, and it does not claim that all semantics have been reviewed. Before corpus import, compare it with the complete metadata-only style inventory from the semantic audit artifact and review representative source examples.

## 29.2 Mapping contract

Each entry records:
- exact marker/style identifier;
- broad semantic category;
- stable semantic key;
- target node/block type from document 26;
- review status.

The initial mapping deliberately uses only target types already described by the structured content model. Where a style needs a more specific representation, preserve its exact source marker and attributes in node metadata rather than inventing a new lossy projection.

## 29.3 Unknown and extended markers

An unknown marker must never be silently dropped, flattened into ordinary Scripture wording, or interpreted as an approved semantic. The resolver emits an `unknown_marker` node retaining:
- original marker identifier;
- all parsed attributes;
- text payload;
- nested children;
- source order;
- pending-review status.

Unknown markers remain available for diagnostics and later registry upgrades. Their content is not rendered as Scripture text by default. A later registry version can add a reviewed mapping without mutating the immutable source archive.

## 29.4 Validation and tests

Run from the repository root:

```bash
python -m unittest discover -s tests/usfm_registry -v
python tools/validate_usfm_marker_registry.py data/usfm/marker-registry.json
```

The validator rejects duplicate identifiers, unsupported categories/node types, missing fields, invalid review states, lossy unknown-marker policies and claims of complete coverage without editorial review. Tests exercise known resolution and exact unknown-marker retention.

## 29.5 Publication gate and next review

This registry is not a publication approval. Before importing or publishing an edition:
1. reconcile the registry against the actual WEBP/KJV style-count report;
2. review every style found in the archives, including extended and nested styles;
3. inspect representative source examples for attributes, milestones, note nesting and ordering;
4. approve each mapping through a named editorial review record;
5. add regression fixtures from source structures with Scripture wording excluded from committed fixtures where licensing requires it.

No Bible text is imported or published by this implementation. R2 activation and source-text import remain separately deferred.
