# 25. Romans 14/16 Versification Review

- **Status:** Source-supported mapping proposal; pending human review and source-scheme unit staging.
- **Reviewed:** 18 November 2026
- **Purpose:** Preserve a source-documented relocation between the WEBP and KJV Romans references without rewriting either edition's native verse addresses.
- **Related:** [Source archive audit](23-source-package-listing-review.md), [USFM import pipeline](15-dual-bible-text-import-pipeline.md), [STEPBible TVTMS](https://github.com/STEPBible/STEPBible-Data).

## 25.1 Finding

The WEBP and KJV source files describe the same relocated passage using different native reference locations:

| WEBP source reference | KJV source reference | Proposed order |
|---|---|---:|
| Romans 14:24 | Romans 16:25 | 1 |
| Romans 14:25 | Romans 16:26 | 2 |
| Romans 14:26 | Romans 16:27 | 3 |

The WEBP source footnote at Romans 14:26 explicitly states that the Textus Receptus places Romans 14:24–26 after Romans 16:24 and numbers them Romans 16:25–27. The KJV source file contains the three consecutive units at Romans 16:25–27. This is direct source evidence for a **three-to-three moved-passage candidate**, not a three-to-two merge and not permission to rewrite either source's references.

The source files audited are:
- WEBP: `75-ROMengwebp.usfm`, from archive SHA-256 `707aea4a010c535af87c6d919f43674f076590d343137eb9f3e264c2b782a424`.
- KJV: `75-ROMeng-kjv.usfm`, from archive SHA-256 `9d37aa78180ceefd5e4aeeaedceccf16f21484e5eb17d5662e8beff31bc3d8a5`.

## 25.2 The WEBP Romans 16:25 footnote anchor

The WEBP source also contains a native verse marker at Romans 16:25 whose content is the relocation footnote, not a second copy of the moved passage. This marker is important source structure.

The importer must:
- preserve the Romans 16:25 marker and its footnote at the source location;
- preserve the three text-bearing units at Romans 14:24–26;
- not count the note-only anchor as a fourth verse in the moved passage;
- not discard the note because its source location overlaps a reference present in KJV;
- retain the original raw USFM and parser provenance.

The current `translation_texts` draft can store empty text and JSON footnote metadata, but it does not yet explicitly distinguish a normal text-bearing verse from an annotation-only marker. Add an explicit content-state field or equivalent validated staging representation before production import. See migration 0005 and the associated regression tests.

## 25.3 Mapping representation

After source-specific units have been staged, represent this proposal as one `scripture_mapping_groups` row with:
- `group_type = 'moved'`;
- three ordered source-side members from the WEBP scheme;
- three ordered target-side members from the KJV scheme;
- explicit provenance to the WEBP source note and the two archive checksums;
- `confidence = 'medium'` and `review_status = 'pending'` until editorial review.

Do not insert the mapping group before the corresponding source units exist. Do not approve it automatically because the source note is explicit. Optional pairwise mapping edges may be added after review, preserving the ordered one-to-one sequence, while the group remains classified as a moved passage.

The machine-readable proposal is maintained at [`data/versification/proposals/romans-14-24-26-to-16-25-27.json`](../data/versification/proposals/romans-14-24-26-to-16-25-27.json). Its scheme codes are provisional placeholders, not database IDs.

## 25.4 Supporting crosswalk context

The [STEPBible TVTMS dataset](https://github.com/STEPBible/STEPBible-Data/blob/5de0a47f35f0fc13dfe1430d104e5db8a4285f9c/Versification/TVTMS%20-%20Translators%20Versification%20Traditions%20with%20Methodology%20for%20Standardisation%20for%20Eng%2BHeb%2BLat%2BGrk%2BOthers%20-%20STEPBible.org%20CC%20BY.txt) was inspected at repository commit `5de0a47f35f0fc13dfe1430d104e5db8a4285f9c`; the file's Git blob is `c82082b14dfcd507cd5c899ae88445e04f940360`.

TVTMS is licensed CC BY 4.0. Its notice asks for attribution to Tyndale House and STEPBible.org and a link to the source repository, and asks users not to repost copies of the data file elsewhere. Retain the upstream link and revision rather than copying the full dataset into this repository.

TVTMS is supporting methodology here, not the direct source of a WEBP-specific instruction. The explicit WEBP footnote is the direct evidence for this proposal. Keep the TVTMS version, attribution and any future transformations in provenance metadata.

## 25.5 Acceptance and remaining work

This proposal is not an approved canonical versification decision and does not authorise publication.

Before approval:
1. Materialise independent WEBP and KJV source schemes and exact source units from the checksummed archives.
2. Confirm the three ordered source/target units against the imported semantic representation.
3. Verify that WEBP Romans 16:25 is retained as an annotation-only anchor.
4. Verify that the reader can navigate the moved passage from either edition without changing the displayed native references.
5. Obtain editorial review and record reviewer, date, rationale and decision.
6. Add an integration test for parallel reading, passage links, search results and footnote navigation across the moved passage.

The initial public canon remains the Protestant 66 books. This review does not expand the KJV launch scope to its additional Apocrypha/Deuterocanon books.
