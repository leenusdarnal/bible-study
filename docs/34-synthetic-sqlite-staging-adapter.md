# Synthetic SQLite staging adapter

## Purpose

This adapter tests the import-staging transaction contract without touching Cloudflare D1, R2, or publication systems. It uses a caller-provided SQLite connection and creates only synthetic test tables. The CLI is deliberately limited to an in-memory `--self-test` mode.

## Guardrails

- Run IDs must begin with `synthetic-`; source fingerprints with `synthetic:`.
- Unit identifiers must begin with `fixture:`, and values with `SYNTHETIC_FIXTURE_`.
- Unit records reject additional fields, preventing Scripture text from being passed as payload.
- A batch is one SQLite transaction; an injected failure verifies atomic rollback.
- Identical replays are idempotent. Replays with changed source or payload are rejected.
- Rollback deletes only the selected synthetic run; foreign-key cascade removes its units.
- No Cloudflare credentials, network calls, D1 bindings, R2 operations, or publication operation exist in this module.

## Verification

```sh
python -m unittest discover -s tests/usfm_staging_adapter -v
python tools/scripture_staging_adapter.py --self-test
```

This is a local contract simulator, not a production staging adapter and not authorization to ingest real text.
