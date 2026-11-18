# USFM Batch Conversion Orchestrator

## 32.1 Purpose

The batch orchestrator coordinates the existing source-audit, semantic-audit and one-member structured-conversion components. It creates private structured outputs for the 66-book launch canon and a complete preflight manifest covering every USFM archive member.

It is a local staging utility only. It does not upload archives or canonical USX to R2, write D1 import rows, approve rights or editorial decisions, or publish Scripture.

## 32.2 Inputs

For one source edition, provide:

- The JSON report produced by `scripture_source_audit.py`.
- The metadata-only JSON report produced by `usfm_semantic_audit.py`.
- The extracted directory for the selected source package.
- The marker registry.
- A new, private output directory that does not already exist.

The semantic audit must cover exactly the same source member paths as the source archive inventory. Every extracted member is re-hashed before it is used. Missing, duplicate, unsafe or changed members stop the batch.

## 32.3 Inclusion policy

The orchestrator inventories all source USFM members. A member containing only Protestant-canon book IDs is eligible for conversion. The first release requires exactly one source member per each of the 66 canonical books.

Members outside the 66-book canon are explicitly excluded with a reason. Front matter, glossary and other non-book USFM members with no `\\id` are also explicitly excluded. A member mixing canonical and non-canonical books is not split automatically; it is excluded and requires manual source separation. Duplicate core-book assignments and incomplete 66-book coverage stop the batch.

The full archive inventory is retained in the manifest even though only the 66-book release scope receives structured JSON outputs.

## 32.4 Outputs

The new private output directory contains:

- `converted/<BOOK>.json` — structured Scripture content for each included canonical book.
- `canonical-usx-local/*.xml` — locally generated canonical USX snapshots for source members that passed semantic audit.
- `preflight-manifest.json` — metadata and private relative paths consumed by the preflight engine.

The JSON conversion files and local canonical XML contain Bible text. They must remain in private storage and must never be committed to the repository or uploaded as public CI artifacts.

The manifest records remote canonical-USX object status as pending. Local file creation is not represented as successful R2 storage or immutable-object verification. Archive signature state, rights, marker approval, versification approval and private object storage remain independently gated.

## 32.5 Run

Install the pinned parser and run source and semantic audits first. Then run the batch for one source package:

```bash
python tools/usfm_batch_conversion.py \
  --source-id engwebp \
  --source-audit /private/audit/engwebp-source-audit.json \
  --semantic-audit /private/audit/semantic-audit.json \
  --source-root /private/extracted/engwebp \
  --registry data/usfm/marker-registry.json \
  --output-root /private/batch/engwebp \
  --territory IN
```

Use `eng-kjv` and its matching extracted root/reports for KJV.

The output directory must not already exist. The tool prints a metadata-only summary and exits non-zero if source identity, checksums, semantic coverage, parser evidence or 66-book coverage do not reconcile.

## 32.6 Relationship to preflight

Pass the generated manifest to `scripture_import_preflight.py` with the current rights register, marker registry and versification proposal directory. With the current project state, preflight is expected to remain blocked: local canonical USX files are not verified remote objects, R2 storage is not enabled, and the required rights and editorial approvals remain pending.

A successful batch means only that the local conversion orchestration completed. It is not an import, staging approval or publication decision.
