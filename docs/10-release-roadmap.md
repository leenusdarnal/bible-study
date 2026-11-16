# 10. Release Roadmap

## 10.1 Delivery approach

Build and release small, usable stages. Each stage must be tested and documented before expansion. Target progression: private development -> private alpha -> invited beta -> public launch -> continuous improvements.

## 10.2 Phases

### Phase 1 — Foundation
- Set up SvelteKit, TypeScript, Tailwind and Cloudflare Workers.
- Configure D1, Drizzle and migrations.
- Establish design system and responsive shell.
- Set up GitHub Actions and automated quality checks.
- Define environments, secrets and deployment process.

### Phase 2 — Scripture foundation
- Implement canon, books, chapters and verses.
- Build translation and versification registry.
- Import legally distributable text.
- Implement reader navigation and Scripture search.
- Establish stable passage identifiers.

### Phase 3 — Reader and personal library
- Deliver traditional, modern study and parallel reader layouts as translations permit.
- Notes, bookmarks, highlights and reading progress.
- Guest and account experience.
- Offline caching and synchronisation foundation.

### Phase 4 — Study and encyclopedia
- Book/chapter introductions and passage study content.
- People, places and events.
- Cross-reference explorer.
- Search across approved study content.

### Phase 5 — Visual exploration
- Knowledge graph with Cytoscape.js.
- Maps with MapLibre GL JS and licensed/attributed tile sources.
- Chronology and timeline explorer.
- Genealogies and thematic connections.

### Phase 6 — Research and editorial platform
- Research library and source records.
- Licence and attribution registry.
- Staging/import/validation pipeline.
- Specialist review, editor and admin dashboard.
- Community contribution workflow.

### Phase 7 — Advanced capabilities
- Study Academy, courses and reading plans.
- Audio and multimedia.
- Original-language tools.
- Source-grounded AI assistant.
- Advanced research reports and comparison workflows.
- Additional canons and licensed translations.

## 10.3 First public release acceptance principles

The first public release should:
- Provide the complete 66-book framework.
- Display only translations/text that are legally available.
- Allow guests to read and search public content.
- Provide usable study, encyclopedia and cross-reference foundations.
- Include initial people, places, events, maps and timelines.
- Provide personal library features to registered users.
- Work responsively and meet accessibility expectations.
- Have a documented offline strategy.
- Have tested security, backup and recovery basics.
- Clearly label incomplete or unreviewed content.
- Exclude AI from launch.

## 10.4 Quality gates

Before each release:
- Unit and integration tests pass.
- Browser workflows pass in Playwright.
- Type checks, lint and formatting pass.
- Migrations are tested against representative data.
- Permissions are verified server-side.
- Accessibility and responsive layouts are checked.
- Content licences and source attributions are checked.
- Backup restoration and rollback are tested where relevant.

## 10.5 Planning note

Detailed milestones, estimates and issue assignments should be created after the repository architecture and first implementation slice are validated. Do not invent dates before scope and capacity are understood.
