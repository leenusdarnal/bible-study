# 15. Dual Bible Text Import and Validation Pipeline

- **Status:** Proposed implementation design; official archives downloaded, checksummed, structurally audited and all 149 USFM members parsed/round-tripped; versification approval, rights review and D1 publication remain pending.
- **Decision:** Import WEBP and KJV as two distinct translation editions.
- **Target:** Cloudflare R2 + D1 staging and publication workflow.
- **Related:** [Source selection](14-scripture-source-selection.md), [Scripture core implementation](13-scripture-core-implementation-spec.md), [database schema](11-database-schema.md), ADR-006.

## 15.1 Scope and governing rules

The first text corpus will contain two English editions:

1. **WEBP** — World English Bible Protestant Edition, the 66-book subset of the World English Bible Update, source identifier `engwebp`.
2. **KJV** — King James Version, 1769 standardised text, source identifier `eng-kjv`, supplied by eBible.org with Apocrypha/Deuterocanon.

They must be imported as separate editions. Never merge their wording, silently normalise one into the other, or assume that a verse label in one edition identifies the same text boundary in the other.

The first reader release is scoped to the Protestant 66-book canon. For KJV, the raw source archive and staging records may contain additional books; those must remain identifiable and must not be silently deleted. Only the 66-book canon membership is published in the first release. Additional KJV books remain outside the public 66-book view pending a separate canon and product decision.

Core rules:

- Preserve original source archives and checksums.
- Keep source edition, source file, source markers and parser version traceable.
- Treat raw source text as immutable.
- Store parsed text and structured markup without losing semantic distinctions.
- Keep source versification profiles separate until comparison proves a mapping.
- Never publish a translation whose source rights status is unresolved for the intended distribution territories.
- Import failures must not partially publish an edition.

## 15.2 Source register

| Field | WEBP | KJV |
|---|---|---|
| Display name | World English Bible Protestant Edition (WEBP) | King James Version (1769 standardised text) |
| Source ID | `engwebp` | `eng-kjv` |
| Source provider | eBible.org | eBible.org; source credits Crosswire Bible Society and eBible.org |
| Source page | [Edition details](https://ebible.org/find/details.php?id=engwebp) | [Edition details](https://ebible.org/find/details.php?id=eng-kjv) |
| Rights page | [WEBP copyright](https://ebible.org/engwebp/copyright.htm) | [KJV copyright](https://ebible.org/eng-kjv/copyright.htm) |
| Import package | [USFM ZIP](https://ebible.org/Scriptures/engwebp_usfm.zip) | [USFM ZIP](https://ebible.org/Scriptures/eng-kjv_usfm.zip) |
| Alternative | [USFX ZIP](https://ebible.org/Scriptures/engwebp_usfx.zip) | [USFX ZIP](https://ebible.org/Scriptures/eng-kjv_usfx.zip) |
| Stated coverage | 66-book protocanon edition | Includes Apocrypha/Deuterocanon |
| Source text edition | Source page labels the 2020 stable text edition; the online HTML was generated from source files dated 17 Nov 2026 | 1769 standardised text; online HTML generated from source files dated 15 Nov 2026 |
| Release scope | Protestant 66 books | Protestant 66 books only |
| Rights gate | Public-domain notice; do not rename a modified text as WEB | Source says public domain outside UK and notes UK Crown patent printing/import restriction; obtain jurisdiction-specific review before global distribution |

This is a source register, not a legal opinion. Record the exact archive version and rights-page snapshot used for each production import. The source pages can change independently of the underlying text.

## 15.3 Retrieval and immutable archive

For each edition, create a source acquisition record before parsing:

- Translation edition ID and source identifier.
- Exact source page URL and direct archive URL.
- Retrieval timestamp in UTC.
- HTTP response metadata where available (content type, content length, last-modified, ETag).
- SHA-256 checksum of the downloaded archive.
- Archive filename and byte size.
- Rights notice URL, capture date and reviewed territories.
- Import operator and acquisition method.
- Source edition label and any source release date.

Store the original ZIP in a private or restricted R2 source bucket using a content-addressed key, for example:

`source-archives/{translation-edition-id}/{sha256}.zip`

Do not overwrite an archive at the same key. A changed checksum means a new source acquisition and a new import run. Keep the source archive separate from parsed JSON/records and from public reader assets.

**Acquisition status as of 18 Nov 2026:** both official archives were downloaded successfully by GitHub Actions. Their actual byte sizes match the eBible.org file directory; ZIP CRC tests passed; SHA-256, member inventories, book IDs, chapter/verse marker counts and exact primary chapter–verse address differences were generated. The 66 Protestant book IDs are present in each package. The WEBP archive contains 68 USFM members and the KJV archive contains 81; source-only content remains inventoried. The exact checksums and Romans numbering comparison are recorded in [23. Source Package Listing Review](23-source-package-listing-review.md). All 149 USFM members subsequently passed the pinned USFMTC 0.4.10 semantic parse and canonical XML round-trip audit (68 WEBP; 81 KJV; zero review-required files). This closes the initial parser gate for these exact archive checksums, but does not approve verse mappings, territorial rights or publication.

## 15.4 USFM parser design

Use USFM as the common interchange format for both editions. The official USFM documentation has multiple versioned specifications, including 2.5 and 3.x, and describes book identification, chapter and verse markers, headings, paragraphs, poetry, footnotes, cross-references, character styles and attributes. The source scan found no explicit `\\usfm <version>` marker in the USFM members. Do not infer a declared version from the extension. The pinned USFMTC 0.4.10 audit tested USFM 2.5 first and 3.1 only as a fallback; all 149 members passed 2.5. This is a compatibility profile, not a publisher-declared source version.

Parser should be a marker-aware state machine, not a regular expression that strips markers and concatenates everything into plain text.

### Required parser behaviour

1. Read each UTF-8 source file without changing the original bytes held in the archive.
2. Identify the book using the `\id` marker and validate it against the recognised USFM/OSIS book identifier registry.
3. Track current book, chapter, verse, paragraph/poetry context and nested character/note context.
4. Recognise chapter and verse boundaries, including verse bridges, ranges, suffixes and subverse markers where present.
5. Preserve headings, section titles, paragraph markers, poetry line groups, indents, lists and speaker/paragraph context as structured blocks.
6. Preserve footnotes and cross-references as structured inline nodes; do not append their content to the verse body as ordinary words.
7. Preserve character-level markup, divine-name markers, additions, quotation markers and word-level attributes.
8. Preserve source order and raw marker sequence so the parsed representation can be regenerated or audited.
9. Treat unknown markers as retained opaque nodes plus warnings; never silently drop them.
10. Produce deterministic output: the same archive and parser version must produce the same canonical staging representation.

### Initial marker coverage

| Marker family | Examples | Import treatment |
|---|---|---|
| Identification | `\id`, `\h`, `\toc1`, `\toc2`, `\toc3` | Book identity and source book metadata |
| Chapter/verse | `\c`, `\v`, `\ca`, `\va`, `\vp`, `\cp` | Structural boundaries and alternate/published numbering |
| Paragraph/poetry | `\p`, `\m`, `\q1`, `\q2`, `\pi`, `\li` | Layout blocks and line grouping |
| Headings | `\s`, `\s1`, `\ms`, `\d`, `\r` | Separate heading/title blocks |
| Footnotes | `\f`, `\fe`, `\fr`, `\ft`, `\fq`, `\fqa` | Anchored structured note nodes |
| Cross references | `\x`, `\xo`, `\xt`, `\xq` | Anchored reference nodes with unresolved target text retained |
| Character styles | `\add`, `\nd`, `\qt`, `\wj`, `\em` | Inline formatting/semantic spans |
| Word attributes | `\w` and attributes | Preserve attributes; do not infer morphology unless supplied |
| Book extras | `\periph`, introductions and appendices | Preserve as non-verse content and include in source inventory |

The table is an initial coverage target, not an exhaustive list of USFM markers. Maintain a versioned marker registry and test fixtures for all markers found in the actual archives. USFM 3.0 supports alternate chapter and verse numbers through `\ca` and `\va`; these must be captured as alternate numbering metadata rather than folded into the main verse label.

## 15.5 Staging model and import states

Use a durable import-run state machine:

`ACQUIRED → INVENTORIED → PARSED → VALIDATED → REVIEWED → PUBLISHED`

Any stage may instead end in `REJECTED` or `FAILED`, with a recorded reason. Publication is an explicit transaction/operation after all blocking validations pass.

Suggested staging entities (logical names; final physical DDL is a later implementation task):

- `source_acquisitions`: archive URL, retrieval metadata, checksum, rights snapshot.
- `import_runs`: edition, acquisition, parser version, status, start/end times.
- `import_files`: archive member name, file checksum, book identifier, byte count.
- `staged_books`: source book code, recognised work ID, canon eligibility, inventory status.
- `staged_chapters`: source chapter label and order.
- `staged_units`: source verse label, raw label, parsed label, source order and text payload.
- `staged_content_nodes`: headings, paragraphs, poetry, footnotes, cross-references and inline spans.
- `staged_numbering_aliases`: alternate chapter/verse labels and source numbering annotations.
- `import_warnings`: unknown markers, malformed structures, duplicate identifiers and review notes.
- `import_validation_results`: rule, severity, expected value, actual value and outcome.
- `import_publication_events`: who approved publication, when, and which immutable run was promoted.

Do not add unreviewed staging tables to the production schema prematurely. The initial Scripture SQL migration remains the stable domain layer; staging may be implemented as a separate import schema or temporary tables once the application repository is created.

## 15.6 Canon and source-book handling

Book recognition must use identifiers, not filename sorting or display-name matching alone.

- Match `\id` codes to the project's book registry.
- Preserve original source code and filename.
- Reject duplicate book files unless the package explicitly declares a legitimate supplement.
- Record unknown book identifiers as blocking review items.
- The audited WEBP ZIP contains all 66 Protestant book IDs plus `FRT` and `GLO` supplementary IDs. The audit did not find any missing core book ID.
- The audited KJV ZIP contains all 66 Protestant book IDs, 14 Apocrypha/Deuterocanon book IDs and `FRT`. Keep all source entries in the import inventory; publish only the approved 66-book canon in the first reader release.
- Do not count a book as missing merely because its display name differs; use validated identifiers and an explicit alias table.

The 66-book seed already in the repository supplies book identities and order. It does not supply chapter counts, verse counts or text.

## 15.7 Versification and alignment

**Do not declare WEBP and KJV to share an identical versification until their imported source units have been compared.**

Each translation edition initially receives its own source versification profile, even if the observed chapter/verse counts later prove identical for most or all books. For every source unit retain:

- Source book identifier.
- Source chapter label.
- Source verse label exactly as encoded.
- Parsed ordinal and any suffix/subverse component.
- Original source order.
- Optional alternate numbering from USFM markers.
- Stable internal unit ID after validated mapping.

### Candidate crosswalk

The STEPBible Data repository provides a Versification dataset called TVTMS (Translators Versification Traditions with Methodology for Standardisation). The source file describes KJV, Hebrew, Latin and Greek traditions, plus a method for mapping source references to a standard reference. It is licensed CC BY 4.0 and requests attribution to Tyndale House and STEPBible.org with a link to the source repository. The source-confirmed Romans move has been documented separately as a pending three-to-three group: WEBP Romans 14:24–26 to KJV Romans 16:25–27. WEBP also has a note-only Romans 16:25 anchor that must be preserved as footnote metadata, not treated as another text copy. See [25. Romans 14/16 Versification Review](25-romans-versification-review.md) and its [machine-readable proposal](../data/versification/proposals/romans-14-24-26-to-16-25-27.json).

Use TVTMS as a candidate research crosswalk, not as an automatic import truth. Its own documentation explains that verse alignment can involve:
- one source verse mapping to multiple standard units;
- multiple source verses mapping to one standard unit;
- moved or duplicated text represented as subverses;
- absent or empty verse positions;
- passages that should remain merged rather than be forcibly split;
- chapter-level differences and non-verse material such as Psalm superscriptions.

Consequently, a simple `source_verse_id → canonical_verse_id` one-to-one foreign key is insufficient. Migration 0004 adds `scripture_mapping_groups` and ordered `scripture_mapping_group_members` so complete source and target unit sets can represent one-to-one, one-to-many, many-to-one, many-to-many, moved, subverse and absent relationships. Optional `scripture_unit_mappings` pairwise edges are constrained to endpoints already present in the same group. The migration preserves legacy pairwise rows as ungrouped records. This grouped structure was exercised against local D1 in CI run [44250525247](https://github.com/leenusdarnal/bible-study/actions/runs/44250525247).

### Note-only source anchors

A source verse marker can carry a footnote or other annotation without carrying verse wording. The WEBP Romans 16:25 marker is an observed example. Do not silently drop it or publish an empty string as if it were a normal text-bearing verse. Migration 0005 adds `translation_texts.content_state` values for `text`, `annotation_only` and `empty_marker`, with insert/update triggers that enforce the relationship between the text body and annotation metadata. The importer must preserve the note and its native anchor exactly.

**Proposed comparison sequence:**
1. Parse both corpora independently into source-specific staging profiles.
2. Compare book coverage and chapter sequences.
3. Compare verse labels, subverse labels, verse counts and source order by book/chapter.
4. Run known-difference checks from TVTMS, including its documented New Testament KJV/English differences.
5. Compare text-boundary cases and Psalm superscriptions manually.
6. Record exact, split, merged, moved, absent, alternate-number and unresolved mappings.
7. Approve a canonical reference profile only after review; do not choose one just because it is the first imported text.
8. Store the mapping dataset version, source URL, licence attribution, transformation notes and reviewer approval.

TVTMS source file:
[STEPBible Versification / TVTMS](https://github.com/STEPBible/STEPBible-Data/blob/5de0a47f35f0fc13dfe1430d104e5db8a4285f9c/Versification/TVTMS%20-%20Translators%20Versification%20Traditions%20with%20Methodology%20for%20Standardisation%20for%20Eng%2BHeb%2BLat%2BGrk%2BOthers%20-%20STEPBible.org%20CC%20BY.txt)

## 15.8 Validation gates

### Archive gate
- Both archives download successfully from the declared source URLs.
- Archive SHA-256 and byte size are recorded.
- ZIP integrity test passes.
- File inventory is retained.
- Source edition and rights snapshot match the source register.

### Parse gate
- Every expected book file is found exactly once.
- Every `\id` resolves to a known work or a documented extra-book identity.
- Every chapter/verse marker is parsed or reported.
- No unknown marker is silently discarded.
- UTF-8 decoding succeeds; any replacement character or malformed byte is a blocking error.
- Text and markup round-trip or are demonstrably preserved in raw source and structured nodes.

### Content integrity gate
- No unexpected empty books or chapters.
- Duplicate chapter/verse labels are reported and reviewed.
- Verse bridges, suffixes, subverses and alternate numbering are retained.
- Headings, paragraph/poetry blocks, footnotes and cross-references are preserved.
- Text is compared against source-rendered samples for a representative set of books and edge cases.
- Chapter and verse counts are reported per book and compared to independent reference data.

### Alignment gate
- WEBP and KJV have independent source profiles.
- Every automatic mapping has a declared mapping type and provenance.
- Ambiguous or disputed mappings remain unresolved pending review.
- No one-to-one assumption is applied to split/merged/moved cases.
- Canonical scheme decision is recorded in an ADR or approved change to ADR-006.

### Publication gate
- Rights review is complete for intended release territories.
- All blocking validation failures are resolved.
- An editor/reviewer approves the exact import run and checksum.
- Published edition metadata includes attribution and source information.
- Rollback can restore the prior published edition without deleting source archives or user notes.

## 15.9 Import outputs and reports

Each run should produce machine-readable reports:

- `archive-manifest.json`
- `book-inventory.json`
- `parse-summary.json`
- `chapter-verse-counts.csv`
- `marker-coverage.json`
- `unknown-markers.csv`
- `versification-differences.csv`
- `mapping-review.csv`
- `rights-review.json`
- `publication-manifest.json`

The publication manifest must link the public edition to the exact acquisition checksum, parser version, validation report and approved mapping version.

## 15.10 Acceptance criteria for the dual-text corpus

The dual-text corpus is ready for initial release only when:

- Both source archives are acquired, checksummed and preserved.
- Both editions parse independently without unreviewed structural loss.
- WEBP's 66-book coverage is confirmed from the archive, not assumed from the catalogue page.
- KJV's full source inventory is documented and the first-release 66-book scope is explicitly applied.
- Source-specific versification profiles are complete.
- The comparison report identifies all differences and unresolved cases.
- The canonical reference scheme and mapping rules are approved.
- Rights review covers intended publication territories and use cases.
- All published records can be traced to immutable source archives and import runs.

## 15.11 Primary references

- [WEBP edition details and USFM download](https://ebible.org/find/details.php?id=engwebp)
- [WEBP copyright notice](https://ebible.org/engwebp/copyright.htm)
- [KJV edition details and USFM download](https://ebible.org/find/details.php?id=eng-kjv)
- [KJV copyright notice](https://ebible.org/eng-kjv/copyright.htm)
- [USFM 3.0 documentation](https://ubsicap.github.io/usfm/)
- [USFM chapters and verses](https://ubsicap.github.io/usfm/chapters_verses/index.html)
- [USFM footnotes](https://ubsicap.github.io/usfm/notes_basic/fnotes.html)
- [USFM cross-references](https://ubsicap.github.io/usfm/notes_basic/xrefs.html)
- [STEPBible Data repository and CC BY 4.0 terms](https://github.com/STEPBible/STEPBible-Data)
- [STEPBible Versification / TVTMS dataset](https://github.com/STEPBible/STEPBible-Data/tree/5de0a47f35f0fc13dfe1430d104e5db8a4285f9c/Versification)


## 15.12 Archive validation and safe extraction — executed

The official WEBP and KJV USFM archives have now been acquired by the GitHub Actions workflow and passed the checks below:

- HTTPS download from the declared eBible.org URLs.
- Final host validation restricted to eBible.org.
- Response byte count recorded and matched against the official directory snapshot.
- SHA-256 recorded for the exact downloaded bytes.
- ZIP member count, paths, sizes and compression ratios checked.
- Full ZIP CRC test passed for both archives.
- No path traversal, symlink or oversized member was accepted.
- All USFM members decoded as UTF-8 and contained a source \\id marker.
- Complete archive member and marker inventories produced.

The archive hashes, exact sizes, member counts, core book coverage, chapter/verse address counts and workflow run are documented in [23. Source Package Listing Review](23-source-package-listing-review.md).

The audit tool reads USFM members in memory and writes metadata-only reports; it does not write Bible wording or extract files into a public repository. The original ZIP bytes are not stored in this documentation repository or published as a workflow artifact. The workflow runner's temporary source cache is ephemeral.

The archive also contains `keys.asc` and `signature.txt.asc`. Their presence was recorded, but detached-signature verification has not yet been performed. Complete signature verification if the source publisher documents the required verification procedure.

## 15.13 Lossless source representation and schema gap

The current draft Scripture SQL schema stores one text value per edition and Scripture unit, with limited footnote metadata. That is not a sufficient lossless representation of all USFM structures.

Before production import, add a structured content layer capable of preserving:

- source file identity and source byte/character offsets;
- ordered source spans and verse bridges;
- block nodes for headings, paragraphs, poetry, lists and introductions;
- inline nodes for character markers, added words, quotations and divine-name markers;
- nested footnote and cross-reference containers;
- marker names, marker attributes and paired closing markers;
- primary, alternate and published chapter/verse labels;
- source text and normalized search text separately;
- a link from each source span to zero, one or many canonical Scripture units.

A source span does not always equal one canonical verse. A verse bridge, subverse, merged verse, heading, superscription or colophon may need a different representation. Do not flatten these structures into translation_texts and then discard the source representation.

The logical staging model should include at least:

| Logical record | Important fields |
|---|---|
| Source acquisition | source ID, URL, retrieved_at, archive SHA-256, byte size, rights snapshot |
| Import run | acquisition ID, parser version, config hash, status, timestamps |
| Archive member | path, byte size, SHA-256, detected format, book code |
| Staged source unit | book, chapter label, verse label, subverse, order, raw source span |
| Content node | node type, marker, attributes, nesting, source offsets, text |
| Numbering alias | primary/alternate label, chapter/verse relation, source marker |
| Mapping group | source span(s), target unit(s), relation type, order, source, review status |
| Validation finding | rule ID, severity, expected, actual, source location, disposition |
| Publication event | approved run, approver, timestamp, published version |

The exact physical table names and DDL should be reviewed in the application repository before full import. Keep the original archive as the recovery source even after structured nodes are persisted.

## 15.14 Versification dataset findings and attribution

The project inspected the actual STEPBible TVTMS text file through its Git repository. It identifies itself as data for KJV, Hebrew, Latin and Greek traditions and describes both condensed human-readable rules and expanded verse-by-verse mappings.

The data explicitly discusses one-to-one renumbering, split and merged verses, subverses, text moved to another location, duplicated text, absent/empty references, passages that may be missing, different verse starting points and epistle colophons. It also gives KJV-related examples in the New Testament. This is direct evidence that the project must not assume a one-to-one reference conversion.

### Romans 14 / 16 placement: direct TVTMS evidence

The pinned TVTMS file contains a specific record headed `$Rom.14:22-23; 16:24-27`. Its English-standard and KJV columns both place the relevant material at Romans 16:25–27, while a Greek-tradition column records the related text at Romans 14:22–23 and marks the later location as merged/absent. The accompanying note states that the passage at Romans 16:25–27 is found at Romans 14:24–26 in some manuscripts.

This is consistent with the archive scan's observed address sets: WEBP has Romans 14:24–26 and KJV has Romans 16:26–27 (with Romans 16:25 common). It is strong evidence that this is a known passage-placement/versification issue, not a random parser defect. However, TVTMS does not name WEBP as the translation using that profile, and its Greek-tradition column must not be equated with WEBP without source-text review.

**Do not auto-map yet.** Compare the actual three WEBP verse texts with the corresponding KJV Romans 16 text, identify any split/merged boundaries and retain the source-specific addresses. The final mapping should cite both the exact archive checksums and the pinned TVTMS revision.

The file states that it is CC BY 4.0, allows inclusion and reformatting in software, requests attribution to Tyndale House and STEPBible.org with a link to the source repository, and asks users not to post copies of the file elsewhere so that the repository remains the maintained source. Accordingly:

- link to the authoritative STEPBible repository rather than committing a full copy of TVTMS;
- record the inspected Git commit/revision in each import manifest;
- provide the requested attribution wherever the dataset informs published mappings;
- record local transformations and corrections;
- preserve the source mapping label and rationale;
- review mappings rather than blindly applying them.

The source revision inspected during this review was associated with repository commit 5de0a47f35f0fc13dfe1430d104e5db8a4285f9c. Pin the exact file revision used at implementation time; do not assume the branch named master remains unchanged.

## 15.15 Import lifecycle, idempotency and reporting

Use a controlled TypeScript command-line importer for the initial two editions. Do not upload or parse a full corpus through a user-facing request handler. The importer should support dry-run, resumable batches, a validation-only mode and an explicit publish command.

Suggested lifecycle:

    discovered
      -> acquired
      -> checksum_verified
      -> archive_tested
      -> inventoried
      -> parsed
      -> structurally_validated
      -> versification_review
      -> rights_review
      -> approved
      -> published

A run may instead become quarantined, rejected or failed. A failed run must never partially change the currently published edition.

Use an idempotency key derived from source ID, archive SHA-256, parser version and parser configuration hash. An identical rerun must not duplicate staged or published records. A changed archive or parser version creates a new run.

Each run should emit machine-readable artifacts, including:

- archive-manifest.json
- book-inventory.json
- parse-summary.json
- chapter-verse-counts.csv
- marker-coverage.json
- unknown-markers.csv
- versification-differences.csv
- mapping-review.csv
- rights-review.json
- publication-manifest.json

Do not report only a total verse count. Report books, chapters, source verse labels, subverses, bridges, headings, poetry blocks, footnotes, cross-references, colophons, unknown markers, and mapping exceptions separately.

Publication must be an explicit reviewed promotion of one complete run. Retain the previous published version so that rollback does not delete source archives, import history or user notes.

## 15.16 Acceptance checklist and current status

The first dual-edition import is accepted only when all boxes below are supported by recorded evidence:

- [x] WEBP and KJV archives downloaded from their declared source URLs by GitHub Actions.
- [x] Archive SHA-256, actual byte sizes, response metadata and source directory comparison recorded. Immutable R2 keys remain pending because R2 has not been configured.
- [x] ZIP integrity, CRC and safe-member checks pass; the scanner reads members in memory rather than extracting them to disk.
- [x] Every archive member is inventoried and every Scripture file's in-file book code is verified.
- [x] WEBP's 66-book scope is confirmed from the actual archive: all 66 core IDs are present.
- [x] All KJV source book IDs, including 14 Apocrypha/Deuterocanon IDs, are inventoried. The first-release 66-book filter is specified but not yet implemented in a production import.
- [x] Structural scanner passes synthetic fixtures and scans all real USFM members; full semantic-parser tests remain pending.
- [ ] Unknown markers and all structural warnings are resolved or explicitly approved.
- [ ] The source structure is preserved without flattening away USFM semantics.
- [ ] Independent WEBP and KJV source versification profiles are complete and approved; primary address comparison is preliminary only.
- [ ] STEPBible TVTMS revision is pinned, attributed and applied only after editorial review.
- [ ] Split, merged, moved, absent, subverse and alternate-number cases are represented in reviewed mapping groups.
- [x] The draft schema now preserves grouped non-one-to-one mapping membership; migration 0004 applies and a three-to-two mapping group is tested in local D1.
- [ ] The production schema can preserve structured USFM content and approved source mappings.
- [ ] Rights review is recorded for intended publication territories.
- [ ] All blocking validation findings are cleared, including the Romans address divergence.
- [ ] A reviewer approves the exact source checksums and complete semantic import run.
- [ ] D1 publication and rollback are tested.

**Current status (18 Nov 2026):** both official binary archives have been downloaded, SHA-256 checksummed and CRC-validated by the source-audit workflow. All 66 core book IDs are present; WEBP contains 68 USFM members and KJV 81, including KJV Apocrypha/Deuterocanon. The source-level chapter and verse address comparison reveals a Romans placement/numbering difference, recorded in [23. Source Package Listing Review](23-source-package-listing-review.md). Initial semantic parsing and canonical XML round-trip validation are complete for all 149 USFM members. Manual marker review, detached-signature verification, mapping approval, rights review and D1 publication remain open.


## 15.17 Results of the first binary archive audit

The structural audit completed successfully in GitHub Actions. The 66-book chapter counts match at 1,189 in both editions. The audit found 31,103 primary chapter–verse addresses in WEBP and 31,102 in KJV, with 31,100 shared addresses. The only address-set differences are Romans 14:24–26 in WEBP and Romans 16:26–27 in KJV; Romans 16:25 is common. The WEB footnote on [BibleGateway](https://www.biblegateway.com/passage/?search=Romans%2014%3A24-26&version=WEB%3BKJV) describes the Textus Receptus placement of Romans 14:24–26 after Romans 16:24 as 16:25–27. Treat this as a mapping-review lead, not an approved automatic mapping.

The structural scanner did not detect a `\\usfm` version declaration inside the files. Record the source's declared version as unknown/not provided until verified by the publisher or an appropriate parser profile. The scanner also found no verse-range markers or duplicate primary chapter–verse labels, but it is not a complete USFM semantic parser.


### Semantic parser result

The USFM Technical Committee reference parser (`usfmtc 0.4.10`) parsed and round-tripped all 68 WEBP and 81 KJV USFM members under the USFM 2.5 compatibility profile, with zero review-required files and no 3.1 fallback. The source packages contain no declared `\\usfm <version>` marker, so this result is a compatibility finding, not a source-version declaration. See [source audit result 23.13](23-source-package-listing-review.md#2313-semantic-usfm-parsing-and-round-trip-results--completed-18-november-2026) and [audit tool result 24.9](24-source-archive-audit-tool.md#249-semantic-audit-result--18-november-2026).
