# Product Reference: Bible Hub

**Status:** Adopted as a product-design and content-navigation reference  
**Reviewed:** 17 November 2026  
**Project:** Bible Study Repo

## 1. Purpose

Bible Hub is a benchmark for breadth of Bible reference material and rapid navigation from a verse into parallel translations, cross-references, commentaries, interlinear data, lexicons and topical resources.

Official website: https://biblehub.com/

## 2. Observed capabilities

The official homepage and interlinear page reviewed expose:

- Parallel translations and parallel chapter reading.
- Verse-level navigation between parallel, study, audio, visuals, commentary, interlinear, Hebrew/Greek, lexicon and Strong's views.
- Cross-references and Treasury of Scripture Knowledge links.
- Commentaries from a range of historical and modern authors.
- Hebrew and Greek interlinear pages.
- Lexicons, concordances and Strong's-number resources.
- Topical studies, sermons, devotionals and Bible study questions.
- Book overviews, chapter summaries, timelines, maps and visual material.
- Parallel Gospels and harmony-style reading.
- Multilingual Bible navigation.

Bible Hub's terms page states that the terms apply to Bible Hub and supporting sites, was modified 8 September 2025, reserves rights in site content and property, and does not grant an implied licence for commercial use. Individual Bible translations and third-party materials may have separate rights.

## 3. Lessons for Bible Study Repo

### 3.1 Use a consistent passage workspace

Bible Hub makes many resources reachable from a verse. This is useful, but a large number of links can become visually dense.

**Requirement:** build one clean passage workspace with clear tabs or panels: Read, Compare, Cross-references, Study, People & Places, Language and Research.

### 3.2 Keep navigation contextual

A user reading Genesis 1:1 should be able to open its cross-references, relevant commentary, word study and related entities without losing their place.

**Requirement:** maintain the selected passage and scroll position when moving between study panels. Every resource should link back to the passage that opened it.

### 3.3 Present commentary as a comparison of attributed voices

A list of commentators can be useful, but users need to know who wrote each work and when.

**Requirement:** record author, title, publication date/edition, theological or scholarly perspective when known, source, licence and exact passage coverage. Do not merge multiple authors into a single unattributed answer.

### 3.4 Separate content types

Parallel Bible text, commentary, lexicon definitions, sermon material and topical summaries are not interchangeable evidence.

**Requirement:** label each resource type clearly and distinguish primary text, reference work, historical evidence, scholarly interpretation and devotional application.

### 3.5 Keep translation selection rights-aware

The number of translations displayed by a comparator is not a model for our own release rights.

**Requirement:** the translation selector must show only editions we are authorised to display, with rights and attribution metadata managed per edition.

## 4. Proposed feature priorities

| Priority | Feature | Implementation direction |
|---|---|---|
| P0 | Parallel reading | WEBP and KJV only after source validation and import gates |
| P0 | Passage cross-references | Structured references with source attribution |
| P1 | Study panel | Book introductions, passage notes and summaries |
| P1 | Commentary library | Independently licensed or original resources |
| P1 | Dictionary/encyclopedia | Structured entity records linked to Scripture |
| P1 | Timeline and maps | Source-backed chronology and geography |
| P2 | Interlinear/lexicon | Depends on validated and licensed language datasets |
| P2 | Topical and sermon collections | Curated, attributed and editorially reviewed |
| P2 | Audio and visual resources | Licensed media or outbound links |

## 5. Copyright, permissions and reuse boundary

Official terms: https://biblehub.com/terms.htm  
Bible copyright information: https://www.biblehub.com/q/bible_copyright_details.htm

The terms reviewed reserve rights in the website and its content, and state that making services available does not grant an implied licence or a right to commercial use. Bible Hub also notes that copyrighted or “used by permission” materials may require permission from the original publisher.

Therefore:

- Do not scrape or bulk-copy Bible Hub's website, commentary pages, lexicons, images, study notes or other editorial resources.
- Do not assume Bible Hub's presentation of a translation makes that translation reusable.
- Verify each underlying work and translation against its own rights holder and licence.
- Use Bible Hub as a product benchmark and link to its pages where useful.
- Write original summaries and acquire content from independently licensed sources.

This is a product assessment, not legal advice.

## 6. Reference links

- Bible Hub homepage: https://biblehub.com/
- Interlinear Bible: https://biblehub.com/interlinear/
- Terms of Use: https://biblehub.com/terms.htm
- Bible copyright details: https://www.biblehub.com/q/bible_copyright_details.htm
- Commentaries: https://biblehub.com/commentaries/
- Topical Bible: https://biblehub.com/topical/

## 7. Decision

Bible Hub is adopted as a **benchmark for passage-level navigation, parallel reading and breadth of reference resources**. No Bible Hub scraping, copying or dataset import is authorised by this decision.
