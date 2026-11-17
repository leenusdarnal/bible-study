# Competitive Product Benchmark and Consolidated Product Blueprint

**Status:** Research synthesis and recommended product direction  
**Reviewed:** 17 November 2026  
**Project:** Bible Study Repo

## 1. Executive recommendation

Bible Study Repo should combine four complementary strengths while maintaining a distinct identity:

- **Blue Letter Bible:** breadth of reference and study resources.
- **STEP Bible:** contextual original-language and morphology workflows.
- **Bible Hub:** fast passage-level navigation between translations and reference material.
- **YouVersion:** approachable daily reading, personal library, reading plans and offline engagement.

Do not attempt to reproduce all four products feature-for-feature. Build a coherent, Scripture-centred research and learning environment in which every resource is linked to a stable passage or entity, every public claim is traceable to sources, and personal study remains private.

The platform's differentiator should be **a connected, evidence-aware Bible study knowledge base with a beginner-friendly reader**, rather than a large collection of unconnected Bible tools.

## 2. Benchmark comparison

| Product | Strongest benchmark area | Lessons to adopt | Caution |
|---|---|---|---|
| Blue Letter Bible | Study-resource breadth and language tools | Connect commentaries, dictionaries, timelines and original-language tools to Scripture | BLB explicitly prohibits scraping; do not copy resources |
| STEP Bible | Original-language workflow | Reveal vocabulary, interlinear, morphology and lexicon progressively from a passage | Exact data licences and third-party source rights need verification |
| Bible Hub | Passage navigation and parallel resources | Keep parallel translations, cross-references and commentary one click from the verse | Terms reserve rights in site content; individual translations have separate rights |
| YouVersion | Reading engagement and personal library | Resume reading, notes, highlights, plans, audio and offline foundations | Platform API access and each translation's rights require approval |

## 3. Product positioning

**Working positioning:** A Bible reading, study and research platform that helps users move from reading a passage to understanding its context, people, places, themes, language and historical evidence.

### Primary user journeys

1. **Read:** open a book, chapter or passage; choose an authorised translation; adjust reading preferences.
2. **Understand:** view a short overview, context, structure, themes and key terms.
3. **Connect:** follow cross-references and links to people, places, events and related passages.
4. **Investigate:** open commentaries, dictionaries, maps, timelines and cited research.
5. **Study a word:** select a word and view validated original-language data where available.
6. **Remember:** create private notes, highlights, bookmarks and reading plans.
7. **Search:** find a passage, phrase, person, place, theme or research topic.
8. **Continue offline:** read cached, approved text and preserve local study activity until sync is available.

## 4. Recommended information architecture

### Main navigation

- **Home** — Continue Reading, daily passage, reading plans and recent study.
- **Bible** — book/chapter reader, translation selector, parallel view and passage actions.
- **Study** — book introductions, chapter summaries, context, themes, outlines and study guides.
- **Explore** — people, places, events, objects, topics, maps and timelines.
- **Research** — commentaries, dictionaries, manuscripts, archaeology, historical sources and scholarly discussions.
- **Search** — unified search with progressive filters.
- **My Library** — notes, highlights, bookmarks, plans and reading progress.

### Passage workspace

Every passage should provide a stable, consistent workspace with these sections:

| Section | Content |
|---|---|
| Read | Scripture text, headings, footnotes and translation metadata |
| Compare | Side-by-side authorised editions |
| Cross-references | Verse-linked references with source attribution |
| Study | Summary, context, structure, themes and questions |
| People & Places | Linked entity records and maps |
| Language | Lemma, transliteration, morphology and lexicon when supported |
| Research | Commentaries, historical evidence and scholarly claims |
| My Notes | Private notes, highlights and bookmarks |

The selected passage should remain in context as users move between sections.

## 5. Release sequencing

### Release 1 — Complete basic platform

This remains aligned with the agreed initial scope:

- Protestant 66-book Scripture framework.
- WEBP and KJV text editions, only after source, legal and import validation.
- Reader with responsive layout, navigation and reading preferences.
- Parallel reading for the two approved editions.
- Basic passage, reference and phrase search.
- Book introductions, summaries and initial study material.
- Cross-references with provenance.
- Initial biblical people, places and events.
- Initial maps and timelines from approved sources.
- Personal library: notes, highlights, bookmarks and reading progress.
- Guest access and optional user accounts.
- Offline foundation for approved text and private study activity.

### Release 1.1 — Connected study

- Passage workspace and linked study panels.
- Expanded encyclopedia and entity relationships.
- More complete commentary and dictionary library using original or licensed content.
- Reading plans and progress.
- Better search filters and search-result explanations.
- Source and citation detail pages.

### Release 2 — Original-language research

- Greek and Hebrew text editions from approved sources.
- Interlinear alignment.
- Transliteration and lemma display.
- Morphological tagging and plain-language grammar explanations.
- Lexicon and concordance search.
- Word occurrence and cross-corpus search.
- Textual variant comparison where sources and editorial standards are mature.

### Release 3 — Advanced engagement and research

- Audio and video resources with appropriate rights.
- Advanced topical and thematic studies.
- Manuscript and textual criticism resources.
- More detailed historical and archaeological research.
- Optional group or community study features.
- AI-assisted study only after citation, source and editorial controls are mature.

## 6. Product principles

1. **Passage-centred:** Scripture remains the primary navigation anchor.
2. **Progressive disclosure:** simple by default, advanced tools when requested.
3. **Traceability:** claims and resources carry source, version, author, date and citation data.
4. **Evidence categories:** distinguish biblical text, manuscript evidence, archaeology, historical evidence, scholarly conclusions, theological interpretation, inference, dispute and speculation.
5. **Fair representation:** identify interpretive traditions and present significant disagreements accurately.
6. **Rights-aware:** only publish content under a verified licence or explicit permission.
7. **Private by default:** personal notes and highlights are not public editorial content.
8. **Accessible and resilient:** responsive, keyboard-accessible, readable and designed for low-bandwidth/offline use.
9. **Cost-conscious:** favour open standards, free/open-source components and small modular releases.
10. **No premature AI:** AI is a later layer, never a substitute for source quality or editorial review.

## 7. Data and architecture implications

The existing Scripture core and broader data model remain appropriate. The benchmark review reinforces these requirements:

- Stable Scripture units and explicit per-edition versification mappings.
- Passage references that can span chapters and books.
- Resource records for commentary, lexicon, dictionary, study guide, map, timeline and media.
- Source, source version, licence, attribution and rights-holder records.
- Claims and evidence links with citation locations and confidence/review state.
- Entity records for people, places, events, objects and themes.
- Original-language tokens, lemmas, morphology and alignments as separately sourced datasets.
- Reading plans and steps that support multiple passage segments.
- Private notes, highlights, bookmarks and progress separated from public content.
- Offline sync state and conflict-resolution metadata.

Do not force all study content into one generic text field. Keep typed resource records and structured relationships.

## 8. Integration assessment: YouVersion Platform

YouVersion Platform publicly documents a REST API, SDKs and an app-registration/App Key process. It may reduce the cost of integrating licensed Bible versions or a reader component.

Recommended action:
1. Register or review the developer portal.
2. Read API usage, SDK and platform terms.
3. Confirm app eligibility and access requirements.
4. Ask which Bible editions are available for the intended use and whether display, caching, offline access and redistribution are allowed.
5. Evaluate API quotas, service dependencies, data portability and exit strategy.
6. Build a small proof of concept only after the above checks.

Do not make the initial WEBP/KJV corpus or core reader dependent on YouVersion. Keep the internal Scripture model provider-neutral.

## 9. What not to copy

- Do not scrape or bulk-copy BLB, STEP Bible or Bible Hub.
- Do not assume a translation displayed on a website can be redistributed.
- Do not copy proprietary interface assets, logos, layouts, editorial content or datasets.
- Do not treat a third-party API as a permanent or unrestricted source.
- Do not launch social features before privacy, moderation and abuse controls exist.
- Do not expose morphology or interlinear data without explaining source edition and alignment limitations.
- Do not present a commentary or theological position as neutral fact.

## 10. Open decisions and verification gates

| Item | Current status | Required next action |
|---|---|---|
| WEBP/KJV rights and exact source archives | Candidate source direction documented | Recheck source notices, archive integrity and jurisdiction-specific restrictions |
| USFM parser | Design documented; no production parser | Implement parser, fixtures and lossless round-trip tests |
| Versification crosswalk | Not yet fully validated | Inspect source mapping files and validate edition-specific differences |
| Original-language datasets | Not selected | Identify sources and confirm licences, provenance and text editions |
| Commentary and dictionary corpus | Not selected | Build an independently licensed/original content plan |
| YouVersion Platform | Potential integration only | Review registration, terms, API limits and version-specific licensing |
| Offline behaviour | Foundation in scope | Define local storage, sync and conflict rules |
| AI study features | Deferred | Establish citation-grounding and evaluation gates before implementation |

## 11. Source references

### Product benchmarks
- Blue Letter Bible: https://www.blueletterbible.org/
- Blue Letter Bible permissions: https://www.blueletterbible.org/about/permissions.cfm
- STEP Bible: https://www.stepbible.org/
- Bible Hub: https://biblehub.com/
- Bible Hub terms: https://biblehub.com/terms.htm
- YouVersion Bible App: https://www.youversion.com/bible-app
- YouVersion Platform: https://platform.youversion.com/
- YouVersion developer documentation: https://developers.youversion.com/

### Internal research notes
- [Blue Letter Bible product reference](16-product-reference-blue-letter-bible.md)
- [STEP Bible product reference](17-product-reference-step-bible.md)
- [Bible Hub product reference](18-product-reference-bible-hub.md)
- [YouVersion product reference](19-product-reference-youversion.md)

## 12. Final recommendation

Proceed with the already documented WEBP/KJV source-validation and USFM import work. In parallel, use this blueprint to refine the product experience and data model. Do not begin expensive original-language or media integrations until their data rights and technical requirements are proven.

The first application milestone should be a high-quality passage reader with reliable references, translation switching, cross-references and a private study library. That foundation supports every later benchmark feature without locking the project into another provider's platform.
