# 15. Dual Bible Text Import and Validation Pipeline

- **Status:** Proposed implementation design; source packages not yet downloaded or parsed.
- **Decision:** Import WEBP and KJV as two distinct translation editions.
- **Target:** Cloudflare R2 + D1 staging and publication workflow.
- **Related:** [Source selection](14-scripture-source-selection.md), [Scripture core implementation](13-scripture-core-implementation-spec.md), [database schema](11-database-schema.md), ADR-006.

## 15.1 Scope and governing rules

The first text corpus will contain two English editions:

1. **WEBP** — World English Bible Update, 66-book protocanon edition, source identifier `engwebp`.
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
| Display name | World English Bible Update | King James Version (1769 standardised text) |
| Source ID | `engwebp` | `eng-kjv` |
| Source provider | eBible.org | eBible.org; source credits Crosswire Bible Society and eBible.org |
| Source page | [Edition details](https://ebible.org/find/details.php?id=engwebp) | [Edition details](https://ebible.org/find/details.php?id=eng-kjv) |
| Rights page | [WEBP copyright](https://ebible.org/engwebp/copyright.htm) | [KJV copyright](https://ebible.org/eng-kjv/copyright.htm) |
| Import package | [USFM ZIP](https://ebible.org/Scriptures/engwebp_usfm.zip) | [USFM ZIP](https://ebible.org/Scriptures/eng-kjv_usfm.zip) |
| Alternative | [USFX ZIP](https://ebible.org/Scriptures/engwebp_usfx.zip) | [USFX ZIP](https://ebible.org/Scriptures/eng-kjv_usfx.zip) |
| Stated coverage | 66-book protocanon edition | Includes Apocrypha/Deuterocanon |
| Source text edition | 2020 stable text edition (source page) | 1769 standardised text |
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

**Acquisition status:** the source pages and download links have been verified, but the ZIP archives have not yet been downloaded in this work session. No archive checksum, byte count, file inventory or parsed-book count is claimed. The next implementation run must download both archives and complete the inventory gate before any database import.

## 15.4 USFM parser design

Use USFM as the common interchange format for both editions. The official USFM 3.0 documentation describes book identification, chapter and verse markers, headings, paragraphs, poetry, footnotes, cross-references, character styles and attributes.

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
- For WEBP, expect the declared 66-book protocanon edition.
- For KJV, inventory every supplied book, including Apocrypha/Deuterocanon; map each to a work identity and record whether it belongs to the first-release Protestant 66-book canon.
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

The STEPBible Data repository provides a Versification dataset called TVTMS (Translators Versification Traditions with Methodology for Standardisation). The source file describes KJV, Hebrew, Latin and Greek traditions, plus a method for mapping source references to a standard reference. It is licensed CC BY 4.0 and requests attribution to Tyndale House and STEPBible.org with a link to the source repository.

Use TVTMS as a candidate research crosswalk, not as an automatic import truth. Its own documentation explains that verse alignment can involve:
- one source verse mapping to multiple standard units;
- multiple source verses mapping to one standard unit;
- moved or duplicated text represented as subverses;
- absent or empty verse positions;
- passages that should remain merged rather than be forcibly split;
- chapter-level differences and non-verse material such as Psalm superscriptions.

Consequently, a simple `source_verse_id → canonical_verse_id` one-to-one foreign key is insufficient. The existing unit mapping design must support one-to-many and many-to-one mappings, ordering, mapping type, notes and provenance.

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
[STEPBible Versification / TVTMS](https://github.com/STEPBible/STEPBible-Data/blob/master/Versification/TVTMS%20-%20Translators%20Versification%20Traditions%20with%20Methodology%20for%20Standardisation%20for%20Eng%2BHeb%2BLat%2BGrk%2BOthers%20-%20STEPBible.org%20CC%20BY.txt)

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
- [STEPBible Versification / TVTMS dataset](https://github.com/STEPBible/STEPBible-Data/tree/master/Versification)
