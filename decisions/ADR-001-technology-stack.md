# ADR-001: Technology Stack

- **Status:** Accepted as project direction; individual integrations require validation.
- **Date:** 2026-11-16

## Context

The project requires a responsive public Bible platform, personal accounts, structured research data, offline support, background imports and a future AI research layer. The owner requested Cloudflare services for infrastructure and prefers free/open-source tools initially.

## Decision

Use TypeScript and SvelteKit, Tailwind CSS, shadcn-svelte/Bits UI, Cloudflare Workers, D1, R2, Drizzle ORM, GitHub Actions, Cytoscape.js, MapLibre GL JS, Vitest and Playwright.

Use a modular monolith. Add Queues, Workflows, KV and Durable Objects only for suitable workloads. AI infrastructure is deferred until later phases.

## Consequences

- One main application is easier to build and operate initially.
- D1's SQLite model must shape schema and query design.
- Map tiles/data and Bible translations have independent licensing requirements.
- Authentication integration must be proven before final selection.
- Service limits and pricing must be rechecked before launch.

## Alternatives considered

A separate PostgreSQL service and a microservices architecture were not selected for the initial design because the project prioritises Cloudflare-first infrastructure and operational simplicity.
