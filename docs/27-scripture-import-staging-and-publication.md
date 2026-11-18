# 27. Scripture Import Staging and Publication Contract

- **Status:** Migrations 0001–0007 applied to the live APAC staging D1 database on 18 November 2026; real text staging/import remains pending.
- **Date:** 18 November 2026
- **Purpose:** Define the auditable, repeatable boundary between source archives, parsed import staging and published Scripture text.
- **Related:** [Dual-text import pipeline](15-dual-bible-text-import-pipeline.md), [database schema](11-database-schema.md), [source archive audit](23-source-package-listing-review.md), [Romans versification review](25-romans-versification-review.md).

## 27.1 Design boundary

The project has verified the selected WEBP and KJV source archives and parsed/round-tripped all 149 USFM members. It has **not** imported their Bible text into a live database or published either edition.

Migration `0007_scripture_import_staging.sql` adds a proposed staging/provenance layer to the documentation schema. It is tested against fresh SQLite and temporary local Cloudflare D1 in CI. It is not yet a production migration and has not been applied to a remote D1 database.

The import pipeline has three separate data zones:

1. **Immutable source archive:** the exact ZIP bytes in a restricted R2 bucket, addressed by archive SHA-256. Never overwrite an object when the source changes.
2. **Canonical parse artefacts:** canonical USX per source file in a restricted R2 location, each with its own SHA-256, parser version and compatibility profile.
3. **D1 import staging and published projection:** structured source inventory, source-specific verse-address units, text/annotation projections, validation evidence and controlled publication state.

Do not put complete source ZIPs, parsed Bible wording, canonical USX files or other source text into this public documentation repository or public GitHub workflow artifacts. CI should emit metadata-only audit reports. Real import artefacts belong in controlled storage.

## 27.2 Import-run state machine

Each edition/archive/parser combination receives a distinct immutable import-run identity.

`acquired → inventoried → parsed → validated → reviewed → published`

Any non-terminal state may instead move to `failed` or `rejected`. Those states are terminal; corrections require a new run. A published run is immutable. Rollback is a separate, audited publication operation that restores a previously approved edition state; it does not rewrite the original run history.

| State | Required evidence |
|---|---|
| acquired | Archive URL, restricted R2 object key, byte size, SHA-256, retrieval timestamp, parser package/version/profile, source-edition and manifest metadata |
| inventoried | Safe ZIP checks, complete member inventory, file hashes, recognised/unknown book IDs, expected coverage check |
| parsed | Every included USFM source member has a semantic parser result, canonical USX object key/hash, compatibility profile and per-file structural counts |
| validated | Source units and structured content staged; duplicate/malformed references checked; marker coverage and source-address comparisons recorded; no blocking validation failures |
| reviewed | A named reviewer and approval timestamp; unresolved source/versification/rights questions resolved or explicitly excluded from publication |
| published | Staging promotion and edition availability committed atomically; immutable publication event and rollback reference recorded |

The parser profile is recorded as a compatibility test. Because the selected archives have no publisher-declared `\\usfm` version marker, do not label the source itself “USFM 2.5”. The current audit records that every file passed the USFMTC 0.4.10 USFM 2.5 parser profile.

## 27.3 Physical tables in migration 0007

| Table | Purpose and key invariants |
|---|---|
| `scripture_import_runs` | One run binds edition, source scheme, exact archive URL/object key/hash/size, retrieval time, parser name/version/profile, manifest, status and approval/publication timestamps. Same edition + archive hash + parser/profile combination cannot be duplicated. Source provenance is immutable. |
| `scripture_import_files` | Complete archive-member inventory, source member hash/size, book code/work ID, parse state, declared source version (nullable), tested compatibility profile, canonical USX R2 key/hash and marker counts. A member marked parsed must have a canonical USX key and checksum. |
| `scripture_import_staging_units` | Per-source-unit staging rows with source file, source-specific scheme/work, chapter/unit labels and order, marker order, unit kind, text, annotation metadata, structured content JSON and validation state. Native labels are never silently rewritten. |
| `scripture_import_validation_results` | Append-only machine validation outcomes, severity, rule code and optional source reference. Reports should describe the failure without copying long Bible text into error details. |
| `scripture_import_run_events` | Append-only creation and status-transition history. Published run history and source artefacts are retained. |

The staging-unit content states mirror migration 0005:
- `text`: ordinary text-bearing content; non-empty text is required.
- `annotation_only`: no verse wording at this marker, but footnote/annotation metadata is required.
- `empty_marker`: an explicit empty source marker with neither verse wording nor footnote metadata.

The WEBP Romans 16:25 note-only anchor is the first real source example for `annotation_only`. It must not be discarded or interpreted as a duplicate copy of WEBP Romans 14:24–26.

The staging schema stores a plain-text projection plus structured-content JSON for the D1 import process. The canonical USX R2 object remains the authoritative full parsed source representation, including headings, paragraph/poetry structure, inline character markers, word attributes, footnotes and cross-references. The display/search projection must be reproducible from that canonical representation.

## 27.4 Safety and integrity rules

Migration 0007 enforces the following database-level controls:

- An import run must start in `acquired` and can only follow the declared forward state transitions.
- Source archive hash/URL/object key/size, source scheme, parser identity/profile and manifest are immutable after run creation.
- A parsed source file must point to a canonical USX R2 object and its SHA-256.
- A staging unit must belong to a source file in the same import run and to the run's declared versification scheme.
- The same source reference cannot be duplicated inside a run; source marker order must be unique within its source file.
- Text, annotation-only and empty-marker states must be structurally consistent.
- A run cannot be published if any source file is marked review-required/rejected, any staging unit is not valid, or an error/blocking validation rule has failed.
- Reviewer identity and approval timestamp are mandatory before the run can be marked reviewed or published.
- Published runs, staging units, file inventories, validation evidence and run events cannot be silently edited or deleted.
- A translation edition cannot be switched to `available` before at least one import run for that edition has been published.

The D1 triggers do not replace application-level validation. The publication service must also check rights approval, canon scope, source mapping approval, complete source inventory, canonical USX object presence and successful staging-to-core row materialisation.

## 27.5 Publication transaction

The application must publish one edition/run in a single transactional operation (or a controlled, idempotent workflow if the dataset exceeds one transaction):

1. Confirm the run is `reviewed`, all source/staging validation is green, and the exact archive/parser/scheme are the approved versions.
2. Confirm all canonical USX artefacts exist in the restricted R2 bucket and their hashes match the run manifest.
3. Confirm each staged source reference can be materialised into the run's source-specific `scheme_chapters` and `scripture_units` without changing its original label/order.
4. Insert or upsert the corresponding `translation_texts` rows, retaining `content_state`, footnotes and structured content projection; preserve source-to-R2 provenance.
5. Apply only those mapping groups that have a human-approved status. The pending Romans proposal must not be inserted as approved.
6. Verify expected book/chapter/unit counts, unique source addresses, foreign keys, text/annotation states and required marker coverage.
7. Update the import run to `published`, insert the immutable event, update the edition status to `available`, and record the publication manifest—all within the transaction.
8. On any error, roll back the whole transaction. Do not leave a partly available translation.

For a new edition version, keep the previous published run available until the new run has passed every gate. Promotion and rollback must not cascade-delete notes, bookmarks, highlights, reading progress or passage references.

## 27.6 Idempotency and reprocessing

- The same edition + archive SHA-256 + parser name/version/profile is one logical import identity.
- Re-running a completed parse should reuse verified content-addressed artefacts, not produce duplicate source units.
- A new source archive hash creates a new run, even if the human-readable edition name has not changed.
- A parser-version/profile change creates a new run against the same immutable source archive. Compare output hashes/counts and marker-level differences before promoting it.
- Never edit the source archive or previous published artefacts in place.
- A new import must not overwrite user-owned annotations or personal reading data.

## 27.7 Cloudflare and deployment boundary

The connected Cloudflare account currently has no D1 database for this project. GitHub Actions has successfully applied migrations 0001–0007 to ephemeral local D1 during CI, but there is no remote project D1 deployment, R2 source bucket or application Worker yet.

When the application source repository and environments are established, create separate development/staging and production resources. Apply reviewed migrations in development first, run importer/publication tests, back up production before a schema rollout, and keep raw/canonical Scripture artefacts in restricted R2 storage. Do not upload the source ZIPs to GitHub or public buckets.

## 27.8 Acceptance tests and CI

The migration/test suite must demonstrate:
- initial run creation and event history;
- legal and illegal state transitions;
- immutable archive/parser provenance;
- unique run identity;
- parsed-file canonical USX pointer/hash requirement;
- same-run source file and scheme referential integrity;
- unique source reference and marker order;
- valid text, annotation-only and empty-marker units;
- rejection of unresolved staged units and failed blocking validation;
- reviewer approval requirement;
- published run/staging/evidence/event immutability;
- no edition availability before a published import exists;
- zero foreign-key violations.

CI coverage is implemented in `tests/sqlite/test_scripture_import_staging_migration.py` and the SQLite/D1 workflow. A passing local D1 run validates the draft SQL behaviour; it does not establish a remote database deployment or prove that a real USFM corpus has been imported.
