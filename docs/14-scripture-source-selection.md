# 14. Scripture Source and Initial Text Selection

- **Status:** WEBP and KJV archives acquired, checksummed, structurally audited and semantically parsed/round-tripped (149/149 USFM members); a source-supported Romans mapping proposal is recorded but remains pending review; import and territorial rights gates remain open.
- **Date reviewed:** 2026-11-18
- **Purpose:** Record the selected text editions, source evidence, rights gates and machine-readable source formats.

## 14.1 Selected initial corpus

The project owner selected **both WEBP and KJV** as the initial English text corpus.

1. **World English Bible Protestant Edition (WEBP)** — eBible.org's 66-book protocanon edition.
2. **King James Version (KJV)** — eBible.org's 1769 standardised text edition, whose supplied package includes Apocrypha/Deuterocanon.

The two editions will be imported as separate translation editions using a common USFM parser. Their original archives, source metadata, rights notices, checksums, parser versions and versification profiles must remain distinct.

The first public release remains scoped to the Protestant 66-book canon. KJV source files outside those 66 books must be inventoried and retained in source/staging records; they must not be silently discarded or included in the first public reader.

## 14.2 Candidate comparison and source evidence

| Candidate | Source evidence | Format / coverage | Decision |
|---|---|---|---|
| World English Bible Protestant Edition (WEBP) | eBible.org states public domain and permits copying, redistribution and use; changed text must not be called the unchanged World English Bible | USFM and USFX; 66-book protocanon edition | **Selected** |
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

The source detail and rights pages, archive directory and direct USFM/USFX URLs have been reviewed. Both official USFM ZIP archives were downloaded by the GitHub-hosted source-audit workflow, SHA-256 checksummed, passed ZIP CRC tests and had every member inventoried. The 66 Protestant book IDs were found in both. All 149 USFM members then passed the pinned USFMTC 0.4.10 semantic parse and canonical XML round-trip audit (68 WEBP; 81 KJV). The source text has not been imported into D1. Full evidence is recorded in [23. Source Package Listing Review](23-source-package-listing-review.md).

Before ingestion, record:
- exact source page and direct download URL;
- retrieval timestamp and response metadata;
- archive filename, byte size and SHA-256;
- source edition and rights-notice snapshot;
- complete archive member inventory;
- parser version and import-run identifier.

Preserve each original archive immutably in R2. Do not replace an archive when the source changes; acquire a new version and record a new checksum.

## 14.4 Common import format

Use USFM as the common interchange format. The official USFM documentation publishes multiple versioned specifications, including 2.5 and 3.x. It documents book identification, chapters and verses, alternate numbering, headings, paragraphs, poetry, footnotes, cross-references, character styles and word-level attributes. No `\\usfm <version>` declaration was found in the eBible USFM members. USFMTC 0.4.10 tested USFM 2.5 compatibility first and all 149 members passed that profile; this demonstrates parser compatibility, not a publisher-declared source version.

USFM references:
- [USFM documentation](https://ubsicap.github.io/usfm/)
- [Chapters and verses](https://ubsicap.github.io/usfm/chapters_verses/index.html)
- [Footnotes](https://ubsicap.github.io/usfm/notes_basic/fnotes.html)
- [Cross-references](https://ubsicap.github.io/usfm/notes_basic/xrefs.html)

Use a marker-aware parser. Preserve semantic markup and unknown markers for review; do not flatten all content into plain verse strings. Capture alternate numbering markers such as `\ca` and `\va` separately from primary chapter/verse labels.

## 14.5 Versification strategy

Do not assume the two editions use identical verse boundaries. Import each into its own source-specific versification profile first. Compare book/chapter coverage, verse labels, subverses, alternate numbering and known edge cases before selecting a canonical reference profile.

STEPBible Data is a candidate crosswalk source:
- [STEPBible Data repository (inspected at commit 5de0a47f35f0fc13dfe1430d104e5db8a4285f9c, 2 November 2026)](https://github.com/STEPBible/STEPBible-Data)
- [Versification directory](https://github.com/STEPBible/STEPBible-Data/tree/5de0a47f35f0fc13dfe1430d104e5db8a4285f9c/Versification)
- [TVTMS dataset](https://github.com/STEPBible/STEPBible-Data/blob/5de0a47f35f0fc13dfe1430d104e5db8a4285f9c/Versification/TVTMS%20-%20Translators%20Versification%20Traditions%20with%20Methodology%20for%20Standardisation%20for%20Eng%2BHeb%2BLat%2BGrk%2BOthers%20-%20STEPBible.org%20CC%20BY.txt)

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


## 14.9 Online listing review — 18 November 2026

The current eBible.org HTML reading indexes were inspected in addition to the edition detail pages:

- The [WEBP index](https://ebible.org/engwebp/) identifies this variant as the **World English Bible Protestant Edition**, describes it as a subset of the World English Bible Update and explicitly says it contains only the 66 Old and New Testament books. Its visible navigation lists the 66 canonical book pages, plus front matter and a glossary.
- The [KJV index](https://ebible.org/eng-kjv/) lists the 66 Protestant-canon books and additional Apocrypha/Deuterocanon sections, including Tobit, Judith, Greek Esther, Wisdom, Sirach, Baruch, Daniel additions, Maccabees, Esdras and the Prayer of Manasses. These are additional online sections; do not equate an HTML page count with the ZIP archive's member count.
- The WEBP rights page calls the text public domain, identifies “World English Bible” as a trademark and asks that modified text not be represented under that unchanged name.
- The KJV rights notice describes the 1769-standardised text as public domain outside the UK and notes a letters-patent issue for printing in the UK or importing printed copies into the UK. This wording does not settle every legal question for a globally accessible digital application; obtain jurisdiction-specific advice before UK availability.

**Evidence boundary:** the binary packages have been acquired, structurally audited and semantically round-tripped. Detached signature verification, reviewed versification mappings, territorial rights approval and D1 import remain open. See [23. Source Package Listing Review](23-source-package-listing-review.md) for the audit hashes and results.


## 14.10 Official archive file-directory metadata

The official [eBible.org Scripture file directory](https://ebible.org/scriptures/dir.php), queried on 18 November 2026, listed:
- WEBP USFM archive: 2,908,410 bytes, last modified 2026-11-17 01:18:23.
- KJV USFM archive: 2,771,068 bytes, last modified 2026-11-15 09:36:58.
- WEBP USFX alternative: 3,316,038 bytes, last modified 2026-11-17 01:18:25.
- KJV USFX alternative: 2,825,185 bytes, last modified 2026-11-15 09:37:00.

These are official directory listing values only; no SHA-256 was exposed by the listing. The actual downloaded archive sizes and SHA-256 values are recorded separately in section 23.12. See [23. Source Package Listing Review](23-source-package-listing-review.md) for the full evidence and the independent BibleNLP-derived corpus cross-check.


## 14.11 Semantic parser and Romans mapping review

The pinned USFM Technical Committee reference implementation `usfmtc 0.4.10` parsed and round-tripped all 149 source USFM members: 68 WEBP and 81 KJV. Every file passed the USFM 2.5 compatibility profile; no file required the 3.1 fallback. The archives contain no publisher-declared `\\usfm` version marker, so do not describe 2.5 as the source's declared version. See [semantic audit results](23-source-package-listing-review.md#2313-semantic-usfm-parsing-and-round-trip-results--completed-18-november-2026).

The source files document a moved passage at Romans 14:24–26 / 16:25–27. A pending three-to-three mapping proposal and the WEBP Romans 16:25 footnote-only anchor are recorded in [25. Romans 14/16 Versification Review](25-romans-versification-review.md). This mapping is not approved or seeded as canonical.
