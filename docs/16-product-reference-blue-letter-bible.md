# Product Reference: Blue Letter Bible

**Status:** Adopted as a product-design reference  
**Reference reviewed:** 17 November 2026  
**Project:** Bible Study Repo

## 1. Purpose

Blue Letter Bible (BLB) is adopted as a reference for studying the organisation and discoverability of Bible study tools. It is not a source from which Bible Study Repo may copy website content, scrape datasets, reproduce proprietary presentation, or assume rights to redistribute resources.

Official website: https://www.blueletterbible.org/

Permissions page: https://www.blueletterbible.org/about/permissions.cfm

This document records product observations and translates them into original requirements for Bible Study Repo.

## 2. Observed product capabilities

The BLB homepage and navigation expose the following feature groups:

- Bible reading and translation selection, including KJV, NKJV, NIV and other editions.
- Bible search, multi-verse retrieval, lexical/concordance search and theological FAQ search.
- Text commentaries and audio/video commentaries.
- Bible dictionaries and encyclopedias.
- Book introductions, prefaces, study notes, charts, outlines and timelines.
- Maps and images.
- Topical indexes and curated topical studies.
- Interlinear tools and original-language resources.
- Greek/Hebrew lexical resources, grammars, morphology and concordances.
- Gospel harmony, creeds, catechisms and confessions.
- Reading plans, devotionals, tutorials and learning resources.

The homepage also exposes advanced search filters for canonical ranges and morphological features. The language tools area highlights inline interlinear and Greek inflection tools.

## 3. Lessons to adopt

### 3.1 Organise by study task, not only by content type

Users should be able to start from a passage, a word, a person, a place, a theme or a historical question and move naturally between related resources.

**Our requirement:** every study resource should link to stable Scripture references and relevant entities wherever applicable.

### 3.2 Make original-language tools discoverable

Greek and Hebrew tools should be accessible from the passage and word being studied, rather than hidden in a separate specialist section.

**Our requirement:** provide a progressive path from a readable translation to word-level analysis, lemma, morphology, lexicon entry and source citations. Original-language data must have its own source, edition, licence and provenance records.

### 3.3 Provide layered search

A beginner needs simple phrase and passage search. Advanced users need filters, lexical search, morphology and cross-translation comparison.

**Our requirement:** build simple search first, with advanced filters and specialist search as progressive enhancements.

### 3.4 Connect reference material to Scripture

Commentaries, dictionaries, maps, timelines, introductions and topical studies become more useful when anchored to exact passages.

**Our requirement:** model these as structured, citable resources linked to Scripture units, passage references, people, places, events and themes.

### 3.5 Support multiple learning modes

Reading, listening, watching, comparing, researching and following a reading plan are distinct ways of engaging with Scripture.

**Our requirement:** the roadmap should allow text, audio/video references, study guides and reading plans to coexist without making the first release dependent on expensive media hosting.

### 3.6 Preserve theological transparency

BLB identifies its own theological orientation and notes that materials from a range of evangelical traditions may not all be affirmed by the ministry. This is a useful example of why source perspective and editorial stance should be visible.

**Our requirement:** identify each resource's author, publisher, tradition or perspective when known. Distinguish source description from the platform's own editorial assessment. Represent disagreements fairly and link claims to evidence.

## 4. Features to prioritise for our platform

| Priority | Feature | Bible Study Repo implementation direction |
|---|---|---|
| P0 | Passage-centred study | Bible reader with linked notes, cross-references and entity links |
| P0 | Translation comparison | Parallel reading for approved editions such as WEBP and KJV |
| P0 | Search | Book/chapter/verse, phrase and exact-reference search |
| P1 | Commentaries and study notes | Source-attributed, passage-linked resource records |
| P1 | Dictionaries and encyclopedia | Structured people, places, events, objects and concepts |
| P1 | Maps and timelines | Geographical and chronological records connected to Scripture |
| P1 | Reading plans | Personal plans, progress and reminders |
| P2 | Interlinear and language tools | Original-language text, lemmas, morphology, lexicons and grammar |
| P2 | Advanced lexical search | Search by lemma, morphology, grammatical features and source dataset |
| P2 | Audio/video study resources | Curated, licensed or externally linked media |
| P2 | Gospel harmony and topical studies | Structured thematic and parallel-passage collections |

Priorities are proposed sequencing, not a commitment to reproduce BLB's feature set.

## 5. What we should do differently

Bible Study Repo should not become a collection of disconnected reference pages. Its differentiators should be:

1. **Evidence and provenance first:** every research claim should point to sources, editions, citations and review history.
2. **Clear evidence categories:** distinguish biblical text, manuscript evidence, archaeology, historical evidence, scholarly conclusions, theological interpretation, inference, dispute and speculation.
3. **Multiple perspectives:** describe major interpretive positions fairly, without presenting one tradition's view as universal consensus.
4. **Stable references:** use canonical Scripture identities and explicit versification mappings so notes and links remain stable when a user changes translation.
5. **User-owned study library:** keep notes, highlights, bookmarks and reading progress separate from public editorial content.
6. **Beginner-to-advanced progression:** explain terms and provide simple entry points, while allowing specialist tools to be opened when needed.
7. **Transparent content governance:** display authorship, source date, licence, attribution, editorial status and update history.

## 6. Copyright, permissions and research boundaries

BLB's permissions page states that:
- Linking to BLB pages is permitted without prior permission.
- BLB does not permit scraping content from its websites.
- BLB's own content and third-party authors' materials have different permission requirements.
- Its sharing guidance requires appropriate attribution and prohibits alteration of shared content under the stated permissions.

Therefore:

- Do not scrape BLB pages, crawl the site for bulk extraction, or use automated harvesting to populate our database.
- Do not copy BLB commentaries, dictionaries, notes, articles, media, lexical entries, layouts, logos or other editorial material.
- Do not assume that content displayed freely on BLB is in the public domain.
- We may link to relevant BLB pages as external references, subject to normal link and attribution practices.
- We may independently write original explanations and build original datasets from sources whose licences permit the intended use.
- Before importing any external resource, record its author/publisher, source URL, version/date, licence, attribution requirements, permitted uses and any restrictions.

This document is a product-design assessment, not legal advice. Obtain permission or legal review where rights are uncertain.

## 7. Reference links

- Blue Letter Bible homepage: https://www.blueletterbible.org/
- BLB permissions: https://www.blueletterbible.org/about/permissions.cfm
- BLB language tools: https://www.blueletterbible.org/resources/tools/index.cfm
- BLB commentaries: https://www.blueletterbible.org/commentaries/
- BLB dictionaries: https://www.blueletterbible.org/search/Dictionary/viewEntries.cfm
- BLB timelines: https://www.blueletterbible.org/resources/timelines.cfm
- BLB maps and images: https://www.blueletterbible.org/images/
- BLB Bible study notes: https://www.blueletterbible.org/resources/study-notes.cfm

## 8. Decision

Blue Letter Bible is approved as a **product and information-architecture benchmark only**. Bible Study Repo will implement original designs, original editorial content and independently licensed datasets. No BLB content scraping or bulk copying is authorised by this decision.
