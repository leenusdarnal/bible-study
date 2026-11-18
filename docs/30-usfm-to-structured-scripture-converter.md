# 30. USFM-to-Structured Scripture Converter

- **Status:** Initial deterministic converter implemented; synthetic XML tests and a parser-backed USFM smoke test are wired into CI.
- **Tool:** \`tools/usfm_to_structured_content.py\`
- **Tests:** \`tests/usfm_registry/test_usfm_to_structured_content.py\`
- **Synthetic parser fixture:** \`tests/usfm_registry/fixtures/minimal.usfm\`
- **Related:** [Structured Scripture content model](26-structured-scripture-content-model.md), [Import staging and publication](27-scripture-import-staging-and-publication.md), [USFM marker interpretation registry](29-usfm-marker-interpretation-registry.md).

## 30.1 Purpose and boundary

The converter turns one parsed USFM member into a deterministic JSON staging artefact. It uses the pinned USFM Technical Committee parser (\`usfmtc 0.4.10\`) for USFM input, then converts its USX XML tree into the repository's structured content block/node model.

It is a conversion and validation utility only. It does not upload files, write to D1, create import runs, enable R2, approve rights, approve versification or publish Scripture. The JSON output contains Bible text and must be kept in a private local workspace or restricted staging storage. Never commit actual converted source output or upload it as a public workflow artifact.

## 30.2 Output structure

One input member produces one JSON document containing:

- immutable source metadata: source package ID, original member path, input SHA-256, edition ID, parser package/version/profile and USX version;
- book identity and ordered document-level chapter events;
- ordered content blocks with source marker, block type, source position, chapter label and source attributes;
- flat node rows with deterministic IDs, parent IDs, source marker, node type, source order, unique hierarchical order path, text, raw attributes and registry semantic metadata;
- per-source-verse text projections with native book/chapter/verse labels, annotation count and the content state \`text\`, \`annotation_only\` or \`empty_marker\`;
- marker counts, unresolved marker identifiers, pending marker reviews and readiness status.

Deterministic IDs are derived from the edition, source member, block and node positions. Reprocessing the same bytes with the same converter/registry inputs therefore produces stable record identities and ordering.

## 30.3 Projection rules

- Character-level text is included in its source verse projection.
- Footnote/endnote and cross-reference containers (including their caller and nested character styles) remain in their original structured node trees and are excluded from ordinary verse text.
- A verse marker with annotation content but no verse wording becomes \`annotation_only\`; an explicit marker with neither wording nor annotation becomes \`empty_marker\`.
- Unknown inline marker text is retained in the plain-text projection to avoid silently losing words, but the affected projection is marked for review. Unknown structures are represented as \`unknown_marker\` nodes with source attributes, child nodes and source order preserved.
- Chapter/verse labels are kept source-native, including USX milestone `number` or `sid` values. The converter does not apply cross-edition versification mappings or rewrite source addresses.

The plain-text projection is a convenience for later staging. The structured node rows and original canonical USX remain the structural evidence; the projection does not replace them.

## 30.4 Usage

Install the pinned parser:

\`\`\`bash
python -m pip install "usfmtc==0.4.10"
\`\`\`

Convert one USFM member. Use the exact edition identifier assigned by the staging schema when one exists, and write the output outside the repository:

\`\`\`bash
python tools/usfm_to_structured_content.py /private/source/GEN.usfm \
  --edition-id WEBP \
  --source-id engwebp \
  --source-member GEN.usfm \
  --registry data/usfm/marker-registry.json \
  --output /private/staging/GEN.structured.json
\`\`\`

For an already parsed USX XML file, pass \`--input-format usx\`. The converter calculates the input SHA-256 and accepts an optional \`--source-sha256\` expected value; a mismatch is rejected.

The optional \`--require-reviewed-registry\` switch refuses conversion unless the registry is marked complete and all entries are editorially reviewed. The current registry is intentionally partial and pending review, so normal diagnostic conversion returns a valid structure with \`readiness: review_required\`.

## 30.5 Validation and CI

Run synthetic regression tests:

\`\`\`bash
python -m unittest discover -s tests/usfm_registry -v
\`\`\`

The tests cover:
- book/chapter identity and ordered blocks;
- heading, paragraph and inline-style conversion;
- verse text projection with note bodies excluded;
- annotation-only source units;
- lossless unknown-marker fallback and review flags;
- deterministic IDs/order paths and parent references;
- malformed documents and output-schema validation.

GitHub Actions additionally installs the pinned USFMTC parser and converts a small synthetic USFM fixture into the runner's temporary directory. The fixture contains no sourced Bible text. The temporary output is not uploaded with metadata-only audit artifacts.

## 30.6 Limitations and next gates

- The converter currently handles one source member per invocation; a batch orchestrator and source-manifest integration are separate work.
- The marker registry is not yet exhaustive or editor-approved. Its mappings and unknown-marker cases must be reconciled with the full WEBP/KJV marker inventory before any import readiness decision.
- Some complex USX structures (for example tables, figures and milestones outside the current mapped set) are retained using explicit generic/unknown nodes and require editor review; they are not silently flattened into approved display markup.
- The converter does not assign database work/chapter/unit IDs. A later staging adapter must resolve source book/chapter/verse labels against the correct source-specific versification scheme.
- The pending Romans 14/16 mapping must remain outside conversion and requires separate human approval.
- Rights approval, canonical-USX restricted storage, D1 staging, idempotent batch import and publication controls remain separate gates.

No real WEBP/KJV text has been converted as part of this implementation, and no Scripture text has been written to D1 or published.
