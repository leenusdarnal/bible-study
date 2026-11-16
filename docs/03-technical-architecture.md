# 3. Technical Architecture

## 3.1 Architecture principles

- Cloudflare-first: use Cloudflare services for application hosting and infrastructure wherever technically suitable.
- Modular monolith: keep one deployable application with well-separated domain modules initially.
- Type safety and strict validation.
- Stable identifiers and data provenance.
- Incremental delivery and automated tests.
- Avoid premature service decomposition.
- Keep export and migration paths to reduce platform lock-in.

## 3.2 Confirmed technology baseline

| Layer | Selection |
|---|---|
| Language | TypeScript |
| Application framework | SvelteKit |
| Runtime/hosting | Cloudflare Workers |
| SvelteKit adapter | `@sveltejs/adapter-cloudflare` |
| Styling | Tailwind CSS |
| UI primitives/components | shadcn-svelte + Bits UI |
| ORM | Drizzle ORM |
| Relational database | Cloudflare D1 |
| Object/file storage | Cloudflare R2 |
| Cache/configuration | Cloudflare KV where appropriate |
| Background jobs | Cloudflare Queues and Workflows |
| Coordination/realtime | Durable Objects only where needed |
| Bot protection | Cloudflare Turnstile |
| Graph visualisation | Cytoscape.js |
| Map rendering | MapLibre GL JS |
| Testing | Vitest + Playwright |
| Static analysis/formatting | svelte-check, TypeScript strict mode, ESLint, Prettier |
| Source control | GitHub |
| CI/CD | GitHub Actions |

## 3.3 Application architecture

Use a modular monolith organised by domain. Suggested domains:
- Scripture and translations.
- Reader and personal library.
- Study content and Academy.
- Entities and relationships.
- Geography and chronology.
- Research and sources.
- Editorial and community contributions.
- Identity, roles and privacy.
- Search.
- AI (future module).

Keep business logic out of presentation components. Validate all untrusted inputs on the server and enforce permissions server-side.

## 3.4 Cloudflare responsibilities

- Workers: SvelteKit application and server endpoints.
- D1: structured relational records.
- R2: original imports, permitted documents, media and generated exports.
- KV: suitable cache/configuration use cases, not the authoritative relational store.
- Queues/Workflows: imports, indexing and longer-running background work.
- Durable Objects: introduce only for coordination or realtime use cases that require them.
- Turnstile: bot mitigation for relevant public forms and account flows.
- Workers AI, Vectorize and AI Gateway: later AI phases, not launch dependencies.

## 3.5 D1 design constraints

D1 is SQLite-based. Design for SQLite semantics, supported constraints and indexes. It is not PostgreSQL and does not provide PostGIS. Do not assume PostgreSQL extensions or SQL syntax.

Keep large files in R2, not D1. Use efficient indexed queries and pagination. Validate expected record volume, query patterns and account limits before importing large datasets. Preserve stable IDs and an export/migration strategy. Recheck current D1 limits and pricing at implementation time.

## 3.6 Data flow

External dataset -> R2 source snapshot -> D1 staging metadata and parsed records -> validation/reconciliation -> editorial approval -> approved D1 records -> public application.

Background processing should be idempotent and resumable. Keep source versions, checksums, logs and import outcomes.

## 3.7 Search

Begin with reliable indexed search over Scripture and approved content using a solution compatible with D1/Workers. Evaluate full-text search support and performance against actual requirements. Semantic/vector retrieval belongs to a later AI/research phase.

## 3.8 Authentication

Better Auth is the recommended candidate for email/password, optional social login, 2FA and session management. It is not yet a final implementation commitment: first verify current SvelteKit + Cloudflare Workers + D1 + Drizzle compatibility, security posture, maintenance and migration options in a proof of concept.

## 3.9 Engineering and deployment

- GitHub Actions should run formatting, linting, type checks, unit tests, integration tests and build validation.
- Deploy previews and production to Cloudflare Workers through a controlled workflow.
- Keep secrets in Cloudflare/GitHub secret stores; never commit credentials.
- Use separate development, preview and production resources.
- Apply D1 schema changes through versioned migrations.
- Document rollback and recovery procedures.

## 3.10 Open technical verification

Before implementation, verify:
- Current Cloudflare Workers/SvelteKit adapter requirements.
- D1 limits, backup and restore options.
- Drizzle migration behaviour for D1.
- Authentication library compatibility.
- Map tile source availability, terms and attribution.
- R2 versioning and independent backup options.
- Cloudflare service pricing and free-tier constraints.

Official starting points:
- https://developers.cloudflare.com/workers/framework-guides/web-apps/sveltekit/
- https://developers.cloudflare.com/d1/
- https://developers.cloudflare.com/r2/
- https://orm.drizzle.team/docs/connect-cloudflare-d1
- https://maplibre.org/maplibre-gl-js/docs/
- https://js.cytoscape.org/
- https://www.shadcn-svelte.com/
- https://vitest.dev/
- https://playwright.dev/
