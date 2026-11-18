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
- Two initial English text editions: WEBP and KJV, subject to the documented rights and import-validation gates.
- Legally distributable Bible text, with additional translations added after permissions are secured.
- Bible reading, search and study material.
- Biblical people, places and events.
- Scripture cross-references.
- Initial maps and timelines.
- Personal library features: notes, bookmarks, highlights and chapter-based reading progress trackers.
- Guest-local reading progress and optional accounts; cloud personal records remain private.
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
| [Scripture core implementation specification](docs/13-scripture-core-implementation-spec.md) | Draft SQLite DDL, 66-book seed and validation plan |
| [Scripture source selection](docs/14-scripture-source-selection.md) | Selected WEBP and KJV editions, rights and source formats |
| [Dual-text import pipeline](docs/15-dual-bible-text-import-pipeline.md) | Archive, USFM parsing, staging, versification, validation and publication |
| [Blue Letter Bible product reference](docs/16-product-reference-blue-letter-bible.md) | Product benchmark, feature lessons, original platform requirements and copyright boundaries |
| [STEP Bible product reference](docs/17-product-reference-step-bible.md) | Original-language, interlinear, morphology and guided study benchmark |
| [Bible Hub product reference](docs/18-product-reference-bible-hub.md) | Passage navigation, parallel reading and reference-resource benchmark |
| [YouVersion product reference](docs/19-product-reference-youversion.md) | Reading engagement, personal library, offline and developer platform benchmark |
| [Competitive benchmark and product blueprint](docs/20-competitive-benchmark-and-product-blueprint.md) | Consolidated comparison, information architecture, release priorities and integration recommendations |
| [My Bible Tracker product reference](docs/21-product-reference-my-bible-tracker.md) | Chapter-level progress, multiple trackers, statistics and low-pressure motivation benchmark |
| [Reading Progress Tracker specification](docs/22-reading-progress-tracker-spec.md) | User stories, tracker scope, chapter states, calculations, guest data, privacy and acceptance tests |
| [Source package listing review](docs/23-source-package-listing-review.md) | eBible.org source evidence, archive checksums, ZIP inventory and WEBP/KJV versification comparison |
| [Source archive audit tool](docs/24-source-archive-audit-tool.md) | Reproducible download, ZIP safety, checksum, USFM marker and verse-address audit process |
| [Romans 14/16 versification review](docs/25-romans-versification-review.md) | Source-supported, pending three-to-three moved-passage mapping and note-only WEBP anchor |
| [Structured Scripture content model](docs/26-structured-scripture-content-model.md) | Loss-preserving blocks and nested nodes for USFM-derived headings, paragraphs, poetry, notes and inline markup |
| [Scripture import staging and publication](docs/27-scripture-import-staging-and-publication.md) | Import-run provenance, immutable source inventory, staging validation, guarded publication and rollback requirements |
| [Translation rights register](docs/28-translation-rights-register.md) | Machine-readable translation rights, territory-specific approval and fail-closed publication gate |
| [USFM marker interpretation registry](docs/29-usfm-marker-interpretation-registry.md) | Versioned marker mappings, structured content targets and lossless unknown-marker handling |
| [USFM-to-Structured Scripture Converter](docs/30-usfm-to-structured-scripture-converter.md) | Deterministic USX-to-block/node conversion and source-verse text projections |
| [Scripture import preflight engine](docs/31-scripture-import-preflight-engine.md) | Fail-closed validation of archive coverage, parser provenance, markers, rights, versification and private storage |\n| [USFM batch conversion orchestrator](docs/32-usfm-batch-conversion-orchestrator.md) | Full archive inventory, explicit 66-book inclusion policy, private batch conversion and preflight manifest generation |
| [Scripture import staging coordinator](docs/33-scripture-import-staging-coordinator.md) | Runs fail-closed preflight and creates immutable metadata-only hand-off records; no D1/R2 writes or publication |
| [Architecture decisions](decisions/README.md) | Numbered decision register, statuses and decision history |

SQLite regression tests for the draft reading-progress migration are in `tests/sqlite/` and can be run with `python -m unittest discover -s tests/sqlite -v`. Source audit tests are in `tests/source_audit/` and run with `python -m unittest discover -s tests/source_audit -v`. Translation-rights gate tests are in `tests/rights/` and run with `python -m unittest discover -s tests/rights -v`. USFM marker registry and structured-converter tests are in `tests/usfm_registry/` and run with `python -m unittest discover -s tests/usfm_registry -v`; validate the registry with `python tools/validate_usfm_marker_registry.py data/usfm/marker-registry.json`. Scripture import preflight tests are in `tests/usfm_preflight/` and run with `python -m unittest discover -s tests/usfm_preflight -v`; run the engine with `python tools/scripture_import_preflight.py --manifest <private-manifest.json> --output <private-report.json>`. Batch orchestration tests are in `tests/usfm_batch/`; run them with `python -m unittest discover -s tests/usfm_batch -v`. The batch utility is `tools/usfm_batch_conversion.py`; it validates the complete archive inventory and locally converts only the 66-book launch canon into private staging outputs. The staging coordinator is `tools/scripture_import_staging_coordinator.py`; it creates immutable metadata-only hand-off records after running preflight. Its tests are in `tests/usfm_staging/` and run with `python -m unittest discover -s tests/usfm_staging -v`. The parser-backed converter is `tools/usfm_to_structured_content.py`; it produces private JSON staging output containing Bible text and must not be committed or published. GitHub Actions validates the SQLite regression suites, acquires and audits the official WEBP/KJV archives, semantically parses and round-trips all 149 USFM members, and applies migrations 0001–0007 to a fresh local D1 database. The Cloudflare D1 database `bible-study-staging` has now been created in APAC and migrations 0001–0007 have been applied successfully; the live database contains the 66-book Protestant canon and currently reports zero foreign-key violations. This is a staging schema deployment only: no Bible text has been imported or published. R2 is not yet enabled on the Cloudflare account, so restricted archive/canonical-USX storage and real text staging remain blocked. Versification approval, rights review and application implementation also remain open.

## Status

**Discovery:** 14 rounds completed; product benchmark research expanded across five reference platforms.  
**Current stage:** product requirements and database design, verified WEBP/KJV source archives, structural and semantic USFM validation, a partial marker registry, the deterministic one-member converter, a fail-closed import preflight engine, a private full-archive batch conversion orchestrator, a metadata-only import staging coordinator, local D1 schema regression checks, and source-specific versification review. Real import and publication remain blocked by rights, marker review, signature verification and private R2 storage.  
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

Propose changes through issues or pull requests. Significant architectural changes should include an Architecture Decision Record (ADR) under decisions/.

## License

No repository-wide content or software licence has been selected yet. Individual datasets, Bible translations, research works, images and map sources may have different terms. Do not assume that content in this repository is freely reusable; consult the relevant source and licence records.
