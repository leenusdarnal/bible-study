# Scripture Import Staging Coordinator

## 33.1 Purpose

The coordinator connects the batch-generated preflight manifest to the rights register, marker registry and versification proposal set. It executes the existing fail-closed preflight rules and creates an immutable, metadata-only hand-off record for a future, separately authorized staging operation.

It is an orchestration and evidence-packaging step. It does not perform a D1 import, upload R2 objects, approve a translation licence, authorize an editorial decision or publish Scripture.

## 33.2 Inputs

- A private batch-generated preflight manifest.
- The current translation-rights register.
- The marker interpretation registry.
- The versification proposal directory, if applicable.
- A new output directory that does not already exist.
- An optional operator label for audit attribution.

The preflight engine reads the referenced private conversion JSON to validate structure and verse projections. The coordinator writes only the preflight findings, summary counts, source/edition identity and SHA-256 fingerprints. It never copies Scripture wording into the hand-off.

## 33.3 Run identity and immutability

The coordinator derives a stable run ID from the edition/source identity, archive hash, manifest fingerprint, rights-register fingerprint, marker-registry fingerprint and preflight-report fingerprint.

Each execution creates a new output directory containing:

- `preflight-report.json` — metadata-only result from the established preflight engine.
- `staging-handoff.json` — immutable coordination record, input fingerprints, validation state, finding codes and explicit action controls.

An existing output directory is rejected; records are not overwritten. Re-running identical inputs in a different new directory produces the same deterministic run ID. Any changed source or approval input produces a different identity.

The timestamp and operator label are recorded as audit metadata, but are not part of the deterministic identity.

## 33.4 Handoff states

| State | Meaning |
|---|---|
| `validation_blocked` | One or more blocking preflight findings remain. No staging authorization is possible. |
| `validated` | Preflight has no blocking findings. The hand-off remains `awaiting_manual_staging_authorization`; this is not an automatic import. |

Even a clean preflight requires a named human operator to authorize a distinct staging action after checking restricted object storage, rights and editorial approvals. A future staging service must independently revalidate the fingerprints and authorization at the time of execution.

The hand-off explicitly records that D1, R2, staging authorization and publication authorization are all false. No transition to `reviewed` or `published` is performed by this tool.

## 33.5 Run

```bash
python tools/scripture_import_staging_coordinator.py \
  --manifest /private/batch/engwebp/preflight-manifest.json \
  --rights-register data/rights/translation-rights-register.json \
  --marker-registry data/usfm/marker-registry.json \
  --proposals-dir data/versification/proposals \
  --output-dir /private/staging-handoff/engwebp-run-01 \
  --actor "named-operator-or-service"
```

Exit codes:

- `0`: preflight passed and a hand-off awaiting manual staging authorization was created.
- `2`: a blocked hand-off was created; resolve findings and create a new run.
- `1`: coordination could not safely assemble the hand-off.

Keep the entire batch workspace private because its conversion inputs contain Scripture text. Only metadata-only reports may be considered for ordinary CI artifacts after a separate privacy review.

## 33.6 Current project boundary

Current WEBP/KJV inputs are expected to remain blocked until rights, marker review, source-specific versification, signature verification and restricted object storage are independently satisfied. This coordinator does not bypass those gates and does not enable R2 or write D1.

The next implementation after this coordinator is a separately permissioned, idempotent D1 staging adapter. It must remain disabled until the project explicitly approves real text staging and all upstream controls are satisfied.
