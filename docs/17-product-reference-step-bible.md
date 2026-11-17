# Product Reference: STEP Bible

**Status:** Adopted as a product-design and research-workflow reference  
**Reviewed:** 17 November 2026  
**Project:** Bible Study Repo

## 1. Purpose

STEP Bible is a benchmark for making original-language and cross-reference study available in a passage-centred workflow. It is a reference for product behaviour and research-tool design, not an authorised source for copying its text, datasets, software or interface.

Official website: https://www.stepbible.org/

## 2. Observed capabilities

The official STEP Bible experience and its help prompts expose these capabilities:

- Bible reading with selectable translations and parallel/interlinear arrangements.
- Original-language vocabulary display alongside a selected translation.
- Greek/Hebrew transliteration.
- Interlinear display combining language editions.
- Cross-reference links attached to passages and verses.
- Word-level lookup and vocabulary study.
- Search for occurrences of Hebrew/Greek words.
- Lexicon lookup and Strong's-number discovery.
- Morphological parsing and explanation of grammar codes.
- Comparison of Greek text editions, including NA28, Textus Receptus and SBL editions in supported tools.
- A guided interface that explains how to turn vocabulary and interlinear options on.

The current page reviewed displayed an ESV reading view. The presence of a translation on STEP Bible does not establish that Bible Study Repo may redistribute that translation.

## 3. Lessons for Bible Study Repo

### 3.1 Make the passage the starting point

A user should not need to understand technical terminology before seeing useful study information. Start with a readable passage and let the user reveal language details progressively.

**Requirement:** a passage reader should support a word-level study action that opens transliteration, lemma, morphology, lexicon and related occurrences where validated data exists.

### 3.2 Distinguish translation from original-language source

A reverse interlinear can visually align an English translation with underlying source-language words, but the English word order is not the original-language word order.

**Requirement:** label the selected translation, underlying Greek/Hebrew text edition, alignment method and any uncertainty. Do not imply a one-to-one equivalence where the data does not support it.

### 3.3 Treat morphology as structured data

Grammar labels should be explorable, not opaque abbreviations.

**Requirement:** store the source morphology code and a separately versioned explanatory mapping. Allow a user to open a plain-language explanation of person, number, tense/aspect, voice, mood, case, gender and other applicable categories.

### 3.4 Make cross-references contextual

Cross-references are most useful when attached to the exact verse and grouped or explained by relationship.

**Requirement:** preserve source attribution for each cross-reference set and distinguish direct quotation/allusion, parallel passage, thematic relation and editorial suggestion where the source supports such classification.

### 3.5 Guide beginners

STEP's instructional prompts show that advanced tools need discoverable explanations.

**Requirement:** include short contextual help and a beginner/advanced display mode. Do not overload the default reader with technical data.

## 4. Proposed feature priorities

| Priority | Feature | Implementation direction |
|---|---|---|
| P0 | Passage reading and cross-reference links | Build on the approved WEBP/KJV corpus and canonical reference model |
| P1 | Word selection and study panel | Link only to validated word-level data |
| P1 | Basic lexicon records | Source, edition, licence and editorial provenance required |
| P2 | Interlinear display | Requires properly licensed source-language texts and alignment data |
| P2 | Morphology exploration | Versioned morphology codes and explanatory taxonomy |
| P2 | Word occurrence search | Search index over approved, tagged original-language corpus |
| P2 | Text-edition comparison | Explicitly identify source editions and textual variants |

## 5. Data and licensing boundary

The review did not establish a blanket licence authorising reuse of STEP Bible's website content, software, lexicon entries, tagged datasets or third-party Bible versions. STEP pages may display content from multiple providers and editions, each potentially carrying separate terms.

Therefore:

- Do not scrape or bulk-copy STEP Bible content or datasets.
- Do not treat a resource being viewable online as permission to redistribute it.
- Do not import STEP's lexicon, morphology or tagging data until the exact dataset, owner, licence and redistribution conditions are confirmed in writing or in a clear licence.
- Prefer independently licensed original-language datasets and record their source, version, attribution and permitted use.
- Use STEP Bible as a design reference and link to its pages for external study where appropriate.

This is a product assessment, not legal advice.

## 6. Reference links

- STEP Bible: https://www.stepbible.org/
- STEP Bible translation selector example: https://www.stepbible.org/version.jsp?version=AraSVD
- STEP Bible feedback/help entry point: https://www.stepbible.org/

## 7. Decision

STEP Bible is adopted as a **benchmark for original-language workflows, interlinear presentation, morphology and guided study**. No STEP Bible website scraping, content copying or dataset import is authorised by this decision.
