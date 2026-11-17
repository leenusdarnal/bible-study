# Bible Study Repo

**A Scripture-centred Bible learning, study and research platform.**

This repository is the documentation home and source of truth for the Bible Study Repo project. It records the product vision, requirements, technical architecture, data model, research standards, editorial principles, security decisions and phased delivery plan.

> **Repository scope:** documentation and architecture decisions. The application source code will be maintained separately unless this project is deliberately expanded later.

## Project direction

Bible Study Repo aims to help readers understand Scripture, study passages independently, explore connections across the Bible, and investigate relevant historical, archaeological, textual and theological research.

The platform is designed for beginners, regular Bible readers, teachers, pastors and advanced researchers. Its guiding principle is:

**Simple at first, powerful when needed.**

## Initial release

The first public release is intended to provide a complete basic platform:

- A complete Protestant 66-book Scripture framework.
- Legally distributable Bible text, with additional translations added after permissions are secured.
- Bible reading, search and study material.
- Biblical people, places and events.
- Scripture cross-references.
- Initial maps and timelines.
- Personal library features: notes, bookmarks, highlights and reading progress.
- Optional accounts; public content remains accessible to guests.
- Responsive, accessible design and offline reading capabilities.

AI is deliberately deferred from the first release until the underlying knowledge base, citations and editorial controls are mature.

## Key architectural decisions

- **Frontend/full stack:** SvelteKit + TypeScript.
- **Styling:** Tailwind CSS; shadcn-svelte and Bits UI.
- **Hosting/runtime:** Cloudflare Workers.
- **Database:** Cloudflare D1 with Drizzle ORM.
- **Object storage:** Cloudflare R2.
- **Background processing:** Cloudflare Queues and Workflows where appropriate.
- **Knowledge graph:** Cytoscape.js.
- **Maps:** MapLibre GL JS, with separately licensed and attributed map data/tiles.
- **Testing:** Vitest, Playwright, ESLint, Prettier and svelte-check.
- **Architecture:** modular monolith initially; one central D1 database with a deliberate migration/scaling path.
- **Source control and CI:** GitHub and GitHub Actions.

See [Technical Architecture](docs/03-technical-architecture.md).

## Documentation map

| Document | Contents |
|---|---|
| [Project vision and scope](docs/01-project-vision-and-scope.md) | Mission, audiences, principles and first-release scope |
| [Product experience](docs/02-product-experience.md) | Navigation, homepage, Bible reader, study and exploration |
| [Technical architecture](docs/03-technical-architecture.md) | Stack, Cloudflare services and engineering standards |
| [Data model](docs/04-data-model.md) | Scripture, entities, relationships, research and stable IDs |
| [Content and research governance](docs/05-content-research-governance.md) | Import pipeline, sources, editorial review and contributions |
| [Theological and editorial principles](docs/06-theological-editorial-principles.md) | Interpretive approach and treatment of disagreement |
| [AI standards](docs/07-ai-standards.md) | Future AI assistant, grounding, citations and controls |
| [Security, privacy and operations](docs/08-security-privacy-operations.md) | Roles, authentication, privacy, backups and recovery |
| [Licensing and attribution](docs/09-licensing-attribution.md) | Translation rights, datasets and provenance |
| [Release roadmap](docs/10-release-roadmap.md) | Phases, milestones and acceptance principles |
| [Detailed database schema](docs/11-database-schema.md) | Proposed D1 tables, keys, constraints, indexes and migration slices |
| [Entity relationship diagrams](docs/12-entity-relationship-diagrams.md) | Domain ERDs and cross-domain integrity rules |
| [Architecture decisions](decisions/) | Important decisions and their rationale |

## Status

**Discovery:** 14 rounds completed.  
**Current stage:** database design and implementation planning.  
**Application implementation:** not started in this repository.

Requirements in these documents represent agreed project direction unless explicitly marked as a recommendation, assumption, open question or item requiring verification. Technical limits, licensing terms and third-party integrations must be rechecked before implementation.

## Working principles

1. Scripture references and research claims must be traceable.
2. Biblical text, historical evidence, scholarly conclusions and theological interpretations must be distinguished.
3. Do not publish unlicensed translation text or research material.
4. Preserve original source records, versions and import history.
5. Disputed matters must be represented transparently.
6. Public knowledge must not be confused with private user study data.
7. Build incrementally, test each stage and keep the system maintainable.

## Contributing to the documentation

Propose changes through issues or pull requests. Significant architectural changes should include an Architecture Decision Record (ADR) under `decisions/`.

## License

No repository-wide content or software licence has been selected yet. Individual datasets, Bible translations, research works, images and map sources may have different terms. Do not assume that content in this repository is freely reusable; consult the relevant source and licence records.
