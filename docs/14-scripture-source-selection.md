# 14. Scripture Source and Initial Text Selection

- **Status:** Research completed; initial text choice requires project-owner approval.
- **Date reviewed:** 2026-11-17
- **Purpose:** Select a legally reusable first Bible text and identify reliable machine-readable import sources.

## 14.1 Recommendation

Use the **World English Bible Update, 66-book edition (WEBP)** as the first complete English text corpus, subject to preserving the exact source text and recording its edition/version metadata.

Reasons:
- eBible.org identifies this edition as the 66-book protocanon-only version.
- The source states that the World English Bible is dedicated to the public domain and permits copying, publishing, redistribution and use.
- A downloadable USFM package is available, which is suitable for a structured import pipeline.
- The 66-book subset avoids having to discard deuterocanonical books from the first import.
- The edition's stated 2020 stable text edition provides an identifiable edition label.

The project must preserve the source wording exactly if it continues to call the text the World English Bible. If text is edited, normalised or otherwise changed, preserve the original and label the transformed derivative accurately rather than presenting it as the unchanged WEB text.

**Source pages**
- [WEBP edition details and downloads](https://ebible.org/find/details.php?id=engwebp)
- [WEBP public-domain notice](https://ebible.org/engwebp/copyright.htm)
- [WEBP 66-book text](https://ebible.org/engwebp/)

## 14.2 Candidate comparison

| Candidate | Source evidence | Format / coverage | Assessment |
|---|---|---|---|
| World English Bible Update (WEBP) | eBible.org states public domain | USFM and USFX; 66-book protocanon edition | **Recommended first import** |
| King James Version (KJV) | eBible.org identifies its 1769 standardised text as public domain outside the UK | USFM and USFX; supplied edition includes Apocrypha/Deuterocanon | Good later option; filter to 66 books for Protestant canon and review territorial restrictions |
| NIV | Rights holder permission process | Licensed text | Do not import full text until written permission covers the intended uses |
| NKJV | Rights holder permission process | Licensed text | Do not import full text until written permission covers the intended uses |

The KJV source page notes UK printing/import restrictions associated with the Crown patent, while describing the work as public domain outside the UK. Because the platform may be accessible internationally, review territorial implications before globally distributing a KJV corpus. This document is not a legal opinion.

NIV permissions: https://www.biblica.com/permissions/  
NKJV permissions: https://www.harpercollinschristian.com/sales-and-rights/permissions/

## 14.3 Import source and format

Preferred source for WEBP:
- Edition: World English Bible Update, 66-book protocanon.
- Source identifier: engwebp / WEBP.
- Machine-readable format: USFM package.
- Alternative source format: USFX.
- Source version label: 2020 stable text edition, as stated on the source details page.
- Retrieval date and exact archive checksum must be recorded at the time of import.
- Preserve the original archive in R2; parse into staging before publishing any text rows.

The import must retain:
- Original book identifiers and chapter/verse markers.
- Paragraph and poetry markers where the source encodes them.
- Footnotes and cross-reference markers as structured metadata when feasible.
- Source archive checksum, file names, edition, retrieval date and source URL.
- Parser version and transformation log.

Do not treat the source archive's USFM markers as proof that its versification matches every other translation. Compare actual unit divisions and create explicit mappings where needed.

## 14.4 Versification strategy

Do not hard-code the initial scheme solely because the first translation is WEBP.

Recommended procedure:
1. Import the WEBP USFM archive into a staging parser.
2. Extract book/chapter/verse labels and count units without publishing text.
3. Compare the extracted divisions with a documented standard English versification reference.
4. Inspect known difficult cases and chapter/verse differences.
5. Review STEPBible's versification datasets as a candidate crosswalk resource.
6. Select and document the canonical reference scheme only after the comparison.
7. Store the translation edition's actual source scheme and map it to the canonical scheme where differences exist.

STEPBible Data:
- Repository: https://github.com/STEPBible/STEPBible-Data
- The repository currently describes its data licence as CC BY 4.0 and requests attribution to STEP Bible.
- Its Versification materials describe differences between Hebrew, Greek, Latin and English numbering traditions.
- Use as a candidate reference dataset, not as an unquestioned authority. Record attribution, dataset version, changes and any underlying source/licence conditions.

## 14.5 Source governance

Before import approval:
- Verify the edition and public-domain/licence notice at the source.
- Record the exact source page, download URL, retrieval date and checksum.
- Preserve an immutable copy of the original archive in R2.
- Confirm that all included files belong to the declared edition and licence.
- Keep the raw import, parsed staging data and published records separately identifiable.
- Run validation for missing/duplicate books, chapters and units.
- Do not modify the source text silently.
- Record every normalisation or transformation in an import log.
- Keep translation licensing independent from the licence of metadata or cross-reference datasets.

## 14.6 Decision required

The recommended initial corpus is WEBP, with KJV considered as a subsequent addition after territorial and edition checks. Confirm whether WEBP is acceptable as the first complete public-domain text. If KJV is preferred as the first reader translation, conduct a separate 66-book extraction and jurisdiction review before committing to that source.
