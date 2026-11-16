# 2. Product Experience

## 2.1 Navigation

Use adaptive navigation with a consistent information architecture. Desktop should use a sidebar; mobile should use a compact navigation pattern. Advanced tools should appear contextually rather than overwhelming beginners.

Primary destinations:

1. Home
2. Bible
3. Study
4. Explore
5. Research
6. AI Assistant (future phase)
7. My Library

Navigation and feature density may adapt to user experience level, but core destinations should remain predictable.

## 2.2 Homepage

A combined, customisable dashboard. Users should be able to rearrange, hide and restore sections.

Potential sections:
- Continue reading.
- Daily Scripture.
- Reading plan progress.
- Continue a course or study.
- Recently viewed passages.
- Recommended studies.
- Featured research.
- Explore a person, place or event.
- Recent notes and bookmarks.

Do not require registration merely to view public dashboard content.

## 2.3 Bible reader

Provide three selectable layouts:

### Traditional reader
A clean, distraction-free reading layout with book, chapter and verse navigation.

### Modern study reader
Scripture with contextual tools such as notes, highlights, explanations and cross-references.

### Parallel comparison reader
Side-by-side translations with synchronised passage navigation. Show only translations the platform is legally permitted to display.

Reader layout preference should persist for signed-in users and be locally remembered for guests where practical.

## 2.4 Study experience

Combine integrated study with a dedicated study workspace.

- Integrated study: selecting a verse opens relevant explanations, cross-references, notes and available language information without leaving the reader.
- Study workspace: assemble a passage, references, notes, sources and (in a later phase) AI assistance for deeper investigation.

## 2.5 Study content

Book and chapter resources should progressively include:
- Summary and outline.
- Historical and cultural background.
- Authorship and audience questions, including scholarly disagreement.
- Genre, structure and literary features.
- Major themes.
- People, places and events.
- Cross-references and canonical connections.
- Explanations and important passages.
- Study questions and practical learning prompts.
- Beginner and advanced explanations.

## 2.6 Knowledge exploration

Combine search with interactive visual exploration.

- Search people, places, events, groups, objects, themes, prophecies and passages.
- Open encyclopedia profiles.
- Explore typed relationships in a knowledge graph.
- Explore journeys, regions and sites on maps.
- Investigate events through timelines.
- Explore genealogies, themes, prophecies and Scripture cross-references.

Graph exploration should expand progressively and support filters. Every meaningful relationship should link to evidence and a confidence/evidence classification.

## 2.7 Personal library

For registered users:
- Notes attached to stable Scripture identifiers.
- Highlights.
- Bookmarks.
- Reading progress.
- Saved studies and preferences.
- Personal learning goals and history.

Personal data must remain separate from public knowledge records. Translation switching must not detach notes from their underlying passage.

## 2.8 Study Academy

A progressive curriculum:
1. Introduction to the Bible, canon and translations.
2. The big story of Scripture.
3. How to study a passage.
4. Biblical genres.
5. Old Testament foundations.
6. New Testament foundations.
7. Biblical history and geography.
8. Biblical theology.
9. Advanced research.
10. Independent study.

Support learning paths, reading plans, quizzes and progress tracking.

## 2.9 Appearance and accessibility

Provide light, dark and system themes; adjustable font size and reading fonts; line and paragraph spacing; comfortable reading width; high contrast; keyboard navigation; screen-reader support; responsive layouts; and reduced motion.

Accessibility is a design-system requirement, not a later enhancement.

## 2.10 Offline experience

Offline priorities:
- Bible text that the user is permitted to cache.
- Bookmarks, notes, highlights and reading progress.
- Reading plans and selected study content where licensing allows.

Use a PWA/service-worker approach and IndexedDB. Queue local changes and synchronise on reconnection and app opening; do not rely exclusively on browser Background Sync support. Define conflict handling for simultaneous edits. Research and AI features may require internet.
