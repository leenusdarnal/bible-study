# 14. Scripture Source and Initial Text Selection

- **Status:** Both initial English editions selected; acquisition and validation pending.
- **Date reviewed:** 2026-11-17
- **Purpose:** Record the selected text editions, source evidence, rights gates and machine-readable source formats.

## 14.1 Selected initial corpus

The project owner selected **both WEBP and KJV** as the initial English text corpus.

1. **World English Bible Update (WEBP)** — eBible.org's 66-book protocanon edition.
2. **King James Version (KJV)** — eBible.org's 1769 standardised text edition, whose supplied package includes Apocrypha/Deuterocanon.

The two editions will be imported as separate translation editions using a common USFM parser. Their original archives, source metadata, rights notices, checksums, parser versions and versification profiles must remain distinct.

The first public release remains scoped to the Protestant 66-book canon. KJV source files outside those 66 books must be inventoried and retained in source/staging records; they must not be silently discarded or included in the first public reader.

## 14.2 Candidate comparison and source evidence

| Candidate | Source evidence | Format / coverage | Decision |
|---|---|---|---|
| World English Bible Update (WEBP) | eBible.org states public domain and permits copying, redistribution and use; changed text must not be called the unchanged World English Bible | USFM and USFX; 66-book protocanon edition | **Selected** |
| King James Version (KJV) | eBible.org identifies the 1769 standardised text as public domain outside the UK and notes a UK Crown patent printing/import issue | USFM and USFX; supplied edition includes Apocrypha/Deuterocanon | **Selected, subject to territorial rights review** |
| NIV | Rights holder permission process | Licensed text | Do not import full text until written permission covers intended uses |
| NKJV | Rights holder permission process | Licensed text | Do not import full text until written permission covers intended uses |

**WEBP sources**
- [Edition details and downloads](https://ebible.org/find/details.php?id=engwebp)
- [Public-domain notice](https://ebible.org/engwebp/copyright.htm)
- [USFM archive](https://ebible.org/Scriptures/engwebp_usfm.zip)
- [USFX archive](https://ebible.org/Scriptures/engwebp_usfx.zip)

**KJV sources**
- [Edition details and downloads](https://ebible.org/find/details.php?id=eng-kjv)
- [Copyright notice](https://ebible.org/eng-kjv/copyright.htm)
- [USFM archive](https://ebible.org/Scriptures/eng-kjv_usfm.zip)
- [USFX archive](https://ebible.org/Scriptures/eng-kjv_usfx.zip)

The KJV source notice states that the text is public domain outside the UK, while noting letters-patent restrictions on printing the translation in the UK or importing printed copies into the UK. Because the platform may be globally accessible, obtain jurisdiction-specific legal review before unrestricted KJV distribution. This document is not a legal opinion.

NIV permissions: https://www.biblica.com/permissions/  
NKJV permissions: https://www.harpercollinschristian.com/sales-and-rights/permissions/

## 14.3 Acquisition status

The source detail and rights pages and their USFM/USFX download links have been reviewed. The actual ZIP archives have **not yet been downloaded, checksummed or parsed**. No archive file inventory, checksum, byte size, book count or import validation result is claimed.

Before ingestion, record:
- exact source page and direct download URL;
- retrieval timestamp and response metadata;
- archive filename, byte size and SHA-256;
- source edition and rights-notice snapshot;
- complete archive member inventory;
- parser version and import-run identifier.

Preserve each original archive immutably in R2. Do not replace an archive when the source changes; acquire a new version and record a new checksum.

## 14.4 Common import format

Use USFM as the common interchange format. The official USFM 3.0 documentation describes book identification, chapters and verses, alternate numbering, headings, paragraphs, poetry, footnotes, cross-references, character styles and word-level attributes.

USFM references:
- [USFM documentation](https://ubsicap.github.io/usfm/)
- [Chapters and verses](https://ubsicap.github.io/usfm/chapters_verses/index.html)
- [Footnotes](https://ubsicap.github.io/usfm/notes_basic/fnotes.html)
- [Cross-references](https://ubsicap.github.io/usfm/notes_basic/xrefs.html)

Use a marker-aware parser. Preserve semantic markup and unknown markers for review; do not flatten all content into plain verse strings. Capture alternate numbering markers such as `\ca` and `\va` separately from primary chapter/verse labels.

## 14.5 Versification strategy

Do not assume the two editions use identical verse boundaries. Import each into its own source-specific versification profile first. Compare book/chapter coverage, verse labels, subverses, alternate numbering and known edge cases before selecting a canonical reference profile.

STEPBible Data is a candidate crosswalk source:
- [STEPBible Data repository](https://github.com/STEPBible/STEPBible-Data)
- [Versification directory](https://github.com/STEPBible/STEPBible-Data/tree/master/Versification)
- [TVTMS dataset](https://github.com/STEPBible/STEPBible-Data/blob/master/Versification/TVTMS%20-%20Translators%20Versification%20Traditions%20with%20Methodology%20for%20Standardisation%20for%20Eng%2BHeb%2BLat%2BGrk%2BOthers%20-%20STEPBible.org%20CC%20BY.txt)

The TVTMS file describes KJV, Hebrew, Latin and Greek traditions and explains that alignments may require split, merged, moved, absent and subverse mappings. It identifies its data as CC BY 4.0, requests attribution to Tyndale House and STEPBible.org, and asks users not to repost copies of the dataset elsewhere so that the source remains the single up-to-date version. Record its version, attribution, source link and any transformations. Use it as a reviewed candidate, not as unquestioned authority.

## 14.6 Source governance

- Preserve original archives, checksums and rights snapshots.
- Keep raw archives, parsed staging records and published text separately identifiable.
- Validate book, chapter and verse inventories against source declarations.
- Preserve headings, poetry, footnotes, cross-references and other semantic markup.
- Do not silently modify source wording.
- Record every transformation and parser version.
- Keep translation rights independent from the licence of versification or other metadata datasets.
- Publish only after structural validation, editorial review and rights approval for intended territories.

## 14.7 Next implementation document

See [15. Dual Bible Text Import and Validation Pipeline](15-dual-bible-text-import-pipeline.md) for archive acquisition, USFM parser design, staging states, canon handling, versification comparison, validation gates and publication acceptance criteria.


## 14.8 Detailed versification source review

The STEPBible TVTMS source file has now been inspected, rather than relying only on the repository directory listing. It describes KJV, Hebrew, Latin and Greek traditions and provides both condensed identification rules and expanded mapping records.

The file explicitly documents one-to-one renumbering, subdivided verses, merged verses, subverses, moved or duplicated material, absent and empty positions, text that may be missing, different verse boundaries, passage movement and epistle colophons. Some mappings use suffixes such as a/b or numbered subparts. These examples confirm that a general one-to-one verse crosswalk would be lossy.

The file states that it is CC BY 4.0, allows software inclusion and reformatting, requests attribution to Tyndale House and STEPBible.org with a source link, and asks that copies of the data file not be reposted elsewhere. The project should reference the maintained upstream file, record the exact revision used, provide attribution and document any local transformations. Do not copy the full TVTMS file into this repository.

The inspected repository revision was associated with commit 5de0a47f35f0fc13dfe1430d104e5db8a4285f9c. Pin the actual file revision again when building the importer.

This dataset is a candidate crosswalk, not proof that WEBP follows the KJV profile. The WEBP and KJV archives must each be parsed and evaluated independently. See [15. Dual Bible Text Import and Validation Pipeline](15-dual-bible-text-import-pipeline.md).
