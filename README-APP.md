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

The first UI pass establishes responsive navigation and a Scripture-focused dashboard. The Bible reader, account system, database-backed queries, personal library, offline support and search are not yet wired to services. The homepage's example book cards and reading quote are interface placeholders, not live Bible content.

## Cloudflare deployment

The Worker configuration is a starting point. Before deployment, bind the staging D1 database and later private R2 buckets using Wrangler environment bindings. Do not put API tokens, Bible source archives or licensed translation text in the repository. No production deployment is configured by this branch.
