# 23. Source Package Listing Review — WEBP and KJV

- **Reviewed:** 18 November 2026
- **Status:** Official source pages and online HTML indexes reviewed; binary archive acquisition remains blocked.
- **Purpose:** Record what has been verified before downloading and parsing the two selected USFM source packages.
- **Related:** [Source selection](14-scripture-source-selection.md), [Import pipeline](15-dual-bible-text-import-pipeline.md), [Licensing](09-licensing-attribution.md).

## 23.1 Executive finding

The eBible.org edition pages confirm the direct USFM download links and the rights notices for both selected editions. The online reader indexes corroborate the intended coverage:

- **WEBP:** eBible.org identifies engwebp as its World English Bible Protestant Edition and states that this variant contains only the 66 books of the Old and New Testaments.
- **KJV:** eBible.org identifies eng-kjv as the 1769-standardised King James Version with Apocrypha/Deuterocanon. Its online index lists the 66 Protestant-canon books plus 14 additional apocryphal/additional-corpus page entries.

This does **not** establish the actual ZIP member inventory. The two binary USFM ZIP files have not been acquired, checksummed, opened or parsed in this runtime. No archive checksum, exact archive member count, chapter count, verse count or parser output is claimed.

## 23.2 Official source register

| Item | WEBP | KJV |
|---|---|---|
| Source ID | engwebp | eng-kjv |
| Edition identity | World English Bible Protestant Edition; 66-book subset of the World English Bible Update | King James Version, 1769 standardised text, with Apocrypha/Deuterocanon |
| Official edition page | [eBible WEBP details](https://ebible.org/find/details.php?id=engwebp) | [eBible KJV details](https://ebible.org/find/details.php?id=eng-kjv) |
| Online index | [WEBP reading index](https://ebible.org/engwebp/) | [KJV reading index](https://ebible.org/eng-kjv/) |
| Rights notice | [WEBP copyright](https://ebible.org/engwebp/copyright.htm) | [KJV copyright](https://ebible.org/eng-kjv/copyright.htm) |
| USFM archive | [engwebp_usfm.zip](https://ebible.org/Scriptures/engwebp_usfm.zip) | [eng-kjv_usfm.zip](https://ebible.org/Scriptures/eng-kjv_usfm.zip) |
| USFX alternative | [engwebp_usfx.zip](https://ebible.org/Scriptures/engwebp_usfx.zip) | [eng-kjv_usfx.zip](https://ebible.org/Scriptures/eng-kjv_usfx.zip) |

The edition-detail pages expose the USFM ZIP links directly. Use these exact URLs as the declared acquisition source unless a newer official link is documented.

## 23.3 WEBP index findings

The eBible online index at https://ebible.org/engwebp/ states that the variant is the **World English Bible Protestant Edition** and describes it as a subset of the World English Bible Update containing only the 66 books of the Old and New Testaments.

The visible reading index lists the familiar 66-book Protestant canon, from Genesis through Revelation, together with separate front matter and glossary links. Those supplementary pages are not additional canon books.

The edition details page uses the display heading “World English Bible”, abbreviation WEBP, and source identifier ENGWEBP / engwebp. It identifies the text as public domain and calls the World English Bible name a trademark of eBible.org.

The source materials distinguish the edition label from the current generated site: the details page labels it a “2020 stable text edition”, while the copyright/HTML page was generated on 17 November 2026 from source files dated 17 November 2026. Therefore, acquisition must record the exact archive checksum and retrieval date rather than assuming the ZIP bytes are frozen merely because the text edition is described as stable.

## 23.4 KJV index findings

The eBible online index at https://ebible.org/eng-kjv/ identifies the **King James Version + Apocrypha**. The edition-detail page describes the text as the King James Version or Authorized Version using the standardised 1769 text and with Apocrypha/Deuterocanon.

The online navigation visibly lists the 66 Protestant-canon books and 14 additional apocryphal/additional-corpus section entries:

| Source code in page path | Online index title |
|---|---|
| TOB | Tobit |
| JDT | Judith |
| ESG | Esther (Greek) |
| WIS | Wisdom of Solomon |
| SIR | Sirach |
| BAR | Baruch |
| S3Y | 3 Holy Children's Song |
| SUS | Susanna |
| BEL | Bel and the Dragon |
| 1MA | 1 Maccabees |
| 2MA | 2 Maccabees |
| 1ES | 1 Esdras |
| MAN | Prayer of Manasses |
| 2ES | 2 Esdras |

These are observed online index entries, not verified USFM file names or archive members. The importer must use in-file identifiers, validate any filename-to-book relationship, preserve source-only material, and keep the first public reader restricted to the approved 66-book canon until the canon and rights decision is expanded.

## 23.5 Rights observations

### WEBP

The official WEBP copyright notice says the text is public domain and permits copying, publishing, redistribution and other uses. It also states that “World English Bible” is a trademark and asks that a modified text no longer be represented as the unchanged World English Bible.

Project implications:
- retain the source wording exactly for the published WEBP text;
- if a transformation changes the Bible text itself, do not label the result as the unchanged World English Bible;
- preserve attribution and source edition metadata;
- keep search indexing, tokenisation or display-only formatting transformations separate from edits to the actual text.

### KJV

The eBible KJV notice describes the 1769-standardised text as public domain outside the UK. It also describes letters-patent restrictions concerning printing the translation in the UK or importing printed copies into the UK.

This wording is not a complete legal analysis of the platform's digital distribution model. A globally accessible web application could raise questions beyond the exact printed-copy wording quoted by the source. Obtain jurisdiction-specific advice before enabling KJV distribution in the UK. Do not treat the source page as a blanket legal clearance for every territory or delivery method.

## 23.6 USFM standard and parser implications

The official [USFM documentation](https://ubsicap.github.io/usfm/) publishes versioned specifications, including 2.5 and 3.x documentation. It covers book identification, chapter and verse markers, paragraph and poetry structure, headings, footnotes, cross-references, character styles, attributes and other structured content.

The official [chapters and verses reference](https://ubsicap.github.io/usfm/chapters_verses/index.html) documents chapter and verse syntax and examples. Related references include [footnotes](https://ubsicap.github.io/usfm/notes_basic/fnotes.html), [cross-references](https://ubsicap.github.io/usfm/notes_basic/xrefs.html) and [word-level attributes](https://ubsicap.github.io/usfm/attributes/index.html).

The actual eBible ZIP files were not inspected, so the version marker and the exact marker inventory used in those packages remain unverified. The importer must:
- detect and record the USFM version marker from each source file;
- choose a parser profile compatible with that version;
- preserve raw source files and unknown markers;
- record every marker actually observed;
- add fixtures for real-source edge cases only after archive acquisition and rights review.

Do not assume that the archive uses USFM 3.0 merely because the current documentation site includes 3.x specifications.

## 23.7 Acquisition attempt and limitation

Two retrieval paths were attempted:

1. Firecrawl was asked to inspect the direct ZIP URLs. It returned an explicit unsupported-file-type result for application/zip; it supports pages and common document formats but not binary archive extraction.
2. Direct HTTPS retrieval was attempted from the execution container. DNS resolution for ebible.org failed in that environment, so the files could not be downloaded.

No archive files were created. No checksums or byte sizes are available. This is an environment/network limitation, not a source-page or licence failure.

The archive gate therefore remains open. The next operator must use an environment with eBible.org network access, download each official ZIP, verify the response and ZIP integrity, calculate SHA-256, inventory members, extract safely and then run the parser tests.

## 23.8 Verified versus pending evidence

| Check | Status | Evidence |
|---|---|---|
| Official edition pages exist | Verified | eBible.org edition-detail pages |
| Direct WEBP and KJV USFM URLs published | Verified | Download links on edition-detail pages |
| WEBP online index says 66-book Protestant edition | Verified | WEBP index text |
| KJV online index lists extra Apocrypha/Deuterocanon sections | Verified | KJV index text |
| WEBP public-domain notice inspected | Verified at source-page level | WEBP copyright page |
| KJV territorial notice inspected | Verified at source-page level | KJV copyright page |
| Exact ZIP bytes downloaded | Pending | Network access unavailable in this runtime |
| SHA-256 and archive sizes | Pending | Requires downloaded ZIP files |
| ZIP integrity and safe extraction | Pending | Requires downloaded ZIP files |
| Actual archive member inventory | Pending | Requires downloaded ZIP files |
| Actual in-file book ID and USFM version markers | Pending | Requires downloaded USFM files |
| Chapter/verse counts and parser report | Pending | Requires parsing and validation |
| Rights clearance for all launch territories | Pending | Requires legal review, especially for UK KJV distribution |

## 23.9 Next operational checklist

When archive access is available:

1. Download both archives from the declared HTTPS URLs.
2. Record retrieval timestamp, final URL, content type, content length, ETag and Last-Modified if present.
3. Compute SHA-256 and perform full ZIP integrity checks.
4. Extract safely into separate, new temporary directories.
5. Inventory all members and record each member's size and checksum.
6. Read every Scripture file's in-file book ID and USFM version marker.
7. Compare the WEBP inventory to the 66-book online declaration and the KJV inventory to its 66-book plus supplementary index.
8. Run the parser on all files and generate book/chapter/verse, marker, unknown-marker and structural-integrity reports.
9. Compare source-specific versification profiles and review mappings before selecting the canonical reference scheme.
10. Complete territorial rights review and then approve a specific import run for publication.

**Decision:** retain WEBP and KJV as the selected initial editions, but keep both in an unacquired/unpublished state until the binary archive and legal validation gates are complete.


## 23.10 Official archive directory metadata

The official [eBible.org Scripture file directory](https://ebible.org/scriptures/dir.php) was queried on 18 November 2026. It publishes the following file sizes and last-modified timestamps:

| Archive | Listed size (bytes) | Listed last modified |
|---|---:|---|
| engwebp_usfm.zip | 2,908,410 | 2026-11-17 01:18:23 |
| eng-kjv_usfm.zip | 2,771,068 | 2026-11-15 09:36:58 |
| engwebp_usfx.zip | 3,316,038 | 2026-11-17 01:18:25 |
| eng-kjv_usfx.zip | 2,825,185 | 2026-11-15 09:37:00 |

These are source-directory metadata values, not local measurements. The directory does not expose a SHA-256 checksum in the retrieved listing. The time-zone convention for the displayed timestamps is not explicitly stated in the listing; preserve the values as printed rather than converting them to UTC.

This closes the **source directory metadata** portion of the acquisition checklist. It does not close the archive-download, ZIP integrity, checksum, member inventory or parser gates.

## 23.11 Independent derived-corpus cross-check

The public [BibleNLP/eBible repository](https://github.com/BibleNLP/ebible) was inspected at main commit `2bde52b4c2cfd7056cf4ed07c48969647df79744` (14 November 2026). It describes itself as a curated corpus derived from eBible.org translation packages. Its README states that the source USFM ZIP is obtained from eBible.org and extracted to a verse-per-line corpus.

The README also explicitly states that the extracted files contain **only verse text**: introductory paragraphs, comments, footnotes and other material are removed. Blank lines represent missing source verses; a verse range is kept on its first line and subsequent lines receive the literal `<range>` token. It retains separate per-translation copyright/permission HTML in its metadata/licenses directory.

### Relevant derived files

| Derived file | Size in repository (bytes) | Git blob ID |
|---|---:|---|
| `corpus/eng-engwebp.txt` | 4,024,726 | `6651f1414751516e5239e0d0bf38d52355bef9dd` |
| `corpus/eng-eng-kjv.txt` | 4,896,341 | `d343cefadbf07934940d69850c9198c1ca701ce2` |
| `corpus/eng-eng-kjv2006.txt` | 4,162,183 | `b5fe850467c22a7a971580c36bf05cd529de6f9e` |

The Git blob IDs are repository object identifiers, not SHA-256 hashes of the original eBible ZIP archives.

### Metadata cross-check

The repository's `metadata/translations.csv` snapshot labels both selected eBible projects downloadable and redistributable/public domain. Its records identify project IDs `engWEB2015peb` for WEBP and `engKJV1769eb` for KJV. The KJV row describes the 1769 text with Apocrypha/Deuterocanon and lists 14 additional-corpus books. These are records from the BibleNLP repository's metadata snapshot, not a replacement for the current eBible rights pages.

Its `metadata/verse_counts.tsv` derived-extract statistics report:

| Derived file | Total verse-address rows | Books | OT rows | NT rows | Deuterocanon rows |
|---|---:|---:|---:|---:|---:|
| `eng-engwebp.txt` | 31,090 | 66 | 23,142 | 7,948 | 0 |
| `eng-eng-kjv.txt` | 36,694 | 81 | 23,142 | 7,955 | 5,597 |
| `eng-eng-kjv2006.txt` | 31,097 | 66 | 23,142 | 7,955 | 0 |

The same repository's `translations.csv` has different source-level chapter/verse declarations (WEBP 23,145 OT and 7,958 NT; KJV 23,145 OT, 7,957 NT and 5,720 Deuterocanon verses). This discrepancy is a reason to treat the derived metadata as an independent warning/cross-check, not as the authoritative versification or exact current archive inventory. The extraction is from an earlier source snapshot and transforms verse structures into aligned text lines.

### How this evidence will be used

- Use the files and metadata to identify likely edge cases and to cross-check source verse text/count reports after acquiring the official archives.
- Do not import these derived text files as the platform's canonical Bible corpus. They discard non-verse structure and may encode verse ranges, missing positions and verse references differently from the raw USFM.
- Do not use the BibleNLP repository's overall GitHub `NOASSERTION` licence as a blanket licence for all translation files. The repository says the original source licence applies to each translation and stores per-file notices. Re-check eBible.org's current rights page for publication decisions.
- The separate `eng-kjv2006` entry is a protocanon-only KJV variant with Strong's numbers added. It is not silently substituted for the selected `eng-kjv` source package.

**Evidence boundary:** this is an independently maintained derivative dataset and metadata review. It does not supply the current official USFM ZIP bytes or prove that the present eBible archive matches the derivative corpus snapshot.


## 23.12 Binary archive audit — completed 17 November 2026

The official archives were subsequently downloaded by a GitHub-hosted runner and audited using the repository's metadata-only source audit tool. This supersedes the earlier “archive not acquired” status in sections 23.7–23.9.

### Exact archive results

| Measure | WEBP | KJV |
|---|---:|---:|
| Archive filename | `engwebp_usfm.zip` | `eng-kjv_usfm.zip` |
| Actual archive size | 2,908,410 bytes | 2,771,068 bytes |
| SHA-256 | `707aea4a010c535af87c6d919f43674f076590d343137eb9f3e264c2b782a424` | `9d37aa78180ceefd5e4aeeaedceccf16f21484e5eb17d5662e8beff31bc3d8a5` |
| ZIP entries | 72 | 85 |
| USFM members | 68 | 81 |
| Total uncompressed bytes | 19,094,315 | 13,452,479 |
| ZIP CRC/integrity test | Passed | Passed |
| Actual size matches official directory listing | Yes | Yes |
| Expected Protestant book IDs found | 66 of 66 | 66 of 66 |
| All book IDs found, including front matter/extras | 68 | 81 |
| Chapters across all identified books | 1,189 | 1,362 |
| Primary verse markers across all identified books | 31,103 | 36,822 |

The WEBP archive contains the 66 canonical book IDs plus `FRT` and `GLO` (front matter and glossary). The KJV archive contains the same 66 canonical IDs, 14 Apocrypha/Deuterocanon IDs, and `FRT`. The 14 additional KJV IDs are `1ES`, `1MA`, `2ES`, `2MA`, `BAR`, `BEL`, `ESG`, `JDT`, `MAN`, `S3Y`, `SIR`, `SUS`, `TOB` and `WIS`.

Each package also contains four non-USFM files: `copr.htm`, `keys.asc`, `signature.txt.asc`, and a CSS file (`gentiumplus.css` for WEBP; `latin.css` for KJV). They were inventoried and retained in the metadata report. The presence of key and signature files was noted, but cryptographic signature verification was **not** performed during this audit.

No USFM version declaration matching `\\usfm <version>` was found in the USFM members. The version must therefore remain **not declared / not detected** in the import metadata; do not infer a particular USFM version from the file extension or current online documentation. All USFM members contained a book ID, and no duplicate primary chapter–verse address labels or verse-range markers were detected by the structural scanner.

### Protestant 66-book chapter and verse totals

Both editions have exactly 1,189 chapters over the 66 Protestant-canon book IDs. Their chapter counts match for every one of the 66 books.

| Source | Distinct primary chapter–verse addresses in the 66-book scope |
|---|---:|
| WEBP | 31,103 |
| KJV | 31,102 |
| Common addresses | 31,100 |

The KJV archive has an additional 173 chapters and 5,720 primary verse markers across its 14 additional Apocrypha/Deuterocanon books. These counts are source-marker counts, not a universal statement about the total number of biblical verses under every counting convention.

### Exact primary address differences

The source-address comparison found the following labels only in WEBP:

| Book | Chapter | Verse label |
|---|---:|---:|
| Romans | 14 | 24 |
| Romans | 14 | 25 |
| Romans | 14 | 26 |

The following labels occur only in KJV:

| Book | Chapter | Verse label |
|---|---:|---:|
| Romans | 16 | 26 |
| Romans | 16 | 27 |

Romans 16:25 is a common address in both source profiles. A displayed WEB footnote on [BibleGateway's Romans 14:24–26 page](https://www.biblegateway.com/passage/?search=Romans%2014%3A24-26&version=WEB%3BKJV) states that the Textus Receptus places verses 24–26 after Romans 16:24 as verses 25–27. This is a strong explanation candidate for the observed location/numbering divergence, but the address comparison alone does not prove text equivalence or prescribe an automatic 3-to-2 mapping. A reviewer must compare the actual source passages and the pinned versification crosswalk before approving a mapping group.

**Implementation rule:** keep the WEBP source references and KJV source references distinct. Represent moved, split or combined passage boundaries through reviewed mapping groups with explicit provenance. Do not rename source verse IDs or move source text during ingestion.

### Audit execution evidence

- GitHub Actions workflow: [Scripture source archive audit](https://github.com/leenusdarnal/bible-study/actions/runs/44154558855)
- Commit: `31e71250cdde3dbc2446ef65313db950aa6022fd`
- Final audit unit tests: 9 passed.
- Both archive download and structural audit steps completed successfully.
- Metadata-only workflow artifact: `scripture-source-audit-44154558855`, artifact ID `14360936095`, SHA-256 `475388c6238d4415ee85e9a552a3d60af253302f5a5a64ec0fea32c490a4f97c`.
- The uploaded artifact contains the manifest and CSV inventories, not the original Bible ZIP files or verse wording. GitHub's artifact expiry is 15 February 2027; the archive SHA-256 values above are also recorded in this document.

### Audit boundary and remaining checks

The utility validates the ZIP structure, CRCs, paths, sizes, member inventory, UTF-8 decoding and basic primary `\\id`, `\\c` and `\\v` address structure. It inventories marker frequency and exact primary chapter–verse labels without writing Scripture wording to reports.

It is a structural audit utility, **not** a complete semantic USFM parser. It does not validate every marker's nesting/attributes, prove text round-tripping, verify the detached package signature, decide textual variants, or publish text into D1. A full marker-aware parser and reviewer-led versification reconciliation are still required before import approval.
