# Bible Study application foundation

This branch starts the application layer for the Bible Study project.

## Stack

- SvelteKit 2 and Svelte 5
- TypeScript
- Cloudflare Workers via `@sveltejs/adapter-cloudflare`
- Cloudflare D1 (staging schema already provisioned separately)
- Drizzle ORM (database integration to follow)
- Vitest

## Local development

```sh
npm install
npm run dev
```

Type-check and build:

```sh
npm run check
npm run build
```

## Current implementation

The dashboard and `/bible` catalogue are connected to the staging D1 canon. The Bible page supports searching the 66-book catalogue, filtering by testament, selecting a book and checking for verified chapter structure. Chapter navigation and verse text are intentionally unavailable until a verified versification scheme and rights-cleared translation edition are published. Account features, personal library, reading plans, offline support and passage search remain future work.

## Cloudflare deployment

The Worker configuration is a starting point and includes the staging D1 binding. Before deployment, enable R2 and bind private source buckets using Wrangler environment bindings. Do not put API tokens, Bible source archives or licensed translation text in the repository. No production deployment is configured by this branch.
