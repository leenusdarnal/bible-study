# 31. Scripture Import Preflight and Validation Engine

- **Status:** Fail-closed metadata and converted-output preflight engine implemented; synthetic coverage tests run in GitHub Actions.
- **Tool:** `tools/scripture_import_preflight.py`
- **Tests:** `tests/usfm_preflight/test_scripture_import_preflight.py`
- **Related:** [Source archive audit](24-source-archive-audit-tool.md), [Romans 14/16 versification review](25-romans-versification-review.md), [Structured Scripture content model](26-structured-scripture-content-model.md), [Import staging and publication](27-scripture-import-staging-and-publication.md), [Marker registry](29-usfm-marker-interpretation-registry.md), [USFM converter](30-usfm-to-structured-scripture-converter.md).

## 31.1 Purpose

Preflight is the quality gate between per-member conversion and creation of a validated Scripture import run. It checks the complete declared archive inventory, parser/converter provenance, canonical USX object evidence, source-native verse projections, marker registry approval, territory-specific rights, source-specific versification decisions and private object-storage verification.

It deliberately fails closed. A missing approval or an unverified object is a blocking finding, not a default permission. The report is metadata-only and does not copy verse wording, note bodies or converted content into the report.

## 31.2 Inputs

The CLI consumes four input groups:

1. **Preflight manifest** — a source-audit-derived record containing edition/source IDs, territory, exact archive checksum and size, ZIP integrity, signature review, parser/converter identity, expected source-member count, complete member inventory, per-member parse/round-trip state, canonical USX object key/hash/status, and the private path to each converted JSON output.
2. **Translation rights register** — the current edition-specific record. Its status must be approved for the requested territory, display and cache must be explicitly true, a named reviewer/date/decision reference must exist, and the evidence must identify the exact archive checksum.
3. **Marker registry** — the same registry version used by conversion. Coverage must be complete and editorially reviewed; every encountered marker must be registered and individually reviewed; converted outputs must report no unresolved or pending markers.
4. **Versification proposal directory** — proposals are matched against the source package ID and exact archive checksum. For a native-source-only import, every matching unapproved cross-edition proposal must be explicitly listed as excluded. A cross-edition import is blocked until the applicable proposal is approved.

The manifest also identifies the selected source-specific scheme and its approval. It must not invent a canonical numbering system or rewrite the source's native references. The explicit `required_permissions` list must always include `display`, `cache` and `transform`; `redistribute` must also be listed whenever the selected product delivery requires that additional right.

## 31.3 Manifest contract

The manifest is JSON with `schema_version: 1` and these top-level properties:

| Property | Required content |
|---|---|
| `edition_id`, `source_id` | Supported pair: WEBP / `engwebp` or KJV / `eng-kjv` |
| `territory` | Two-letter uppercase publication territory |
| `source_archive` | Pinned official HTTPS URL, archive SHA-256, positive size, passed ZIP integrity, signature state |
| `parser` | `usfmtc 0.4.10`, compatibility profile 2.5 or 3.1, no inferred publisher-declared version |
| `converter` | Project converter name and pinned version 0.1.0 |
| `expected` | Expected USFM member count and explicit requirement for all 66 Protestant books |
| `archive_members` | Exact complete USFM inventory; each member has its path, uncompressed SHA-256, book IDs, parser/round-trip results, profile, canonical USX object key/hash/status and converted-output path |
| `versification` | Source scheme code, approved state, named reviewer/date/decision, import mode and explicit excluded pending proposal IDs |
| `storage` | Private-bucket assertion and verified immutable archive/canonical-USX object status |

The member inventory is compared with the total expected archive count. Every source member, including material outside the launch canon, must pass parsing and canonical round-trip checks and have a checksum-verified canonical USX object. Each member must be explicitly marked `included` or `excluded`. Only included members require a converted output, and every excluded member requires a reason and an explicit not-for-publication flag. All 66 Protestant-canon books must be included; non-canon book content must be excluded from the initial release. Every included member's converted output must agree with the manifest's edition, source package, source-member path, source checksum, parser profile, converter identity and registry version.

The converted-output path must be relative to the manifest directory and remain inside that directory. The referenced JSON contains Scripture wording and must live in a private workspace. Never commit it or upload it as a public workflow artifact.

## 31.4 Validation rules

The engine currently validates:

- exact source archive URL, checksum format, size and ZIP-integrity result;
- verified detached signature, or a documented reviewer-approved waiver (waiver is reported as a warning);
- pinned parser and converter identity; compatibility profile is not misrepresented as the publisher's declared USFM version;
- expected inventory count, safe unique member names, member SHA-256 and all 66 Protestant book IDs;
- parse and canonical XML round-trip success for every inventoried member;
- per-member converter provenance, source hashes, book identity and marker-registry version;
- complete/reviewed marker coverage and absence of unknown or pending marker mappings;
- structural block/node types, node identifiers, parent-before-child references, unique order paths and increasing source order;
- source-native book/chapter/verse addresses, duplicate address detection and consistent `text`, `annotation_only` and `empty_marker` states;
- rights approval for the requested territory, display/cache permissions, reviewer evidence and exact source archive checksum;
- source-specific versification approval and explicit treatment of matching pending cross-edition mapping proposals;
- private object-storage configuration and verified archive/canonical USX objects.

The 66-book gate is the initial Protestant-canon scope. The complete source ZIP is still inventoried and parsed: WEBP's front matter/glossary and KJV's front matter plus Apocrypha/Deuterocanon books must be recorded as explicitly excluded where outside this release scope. This does not silently approve importing additional KJV books into the first-release canon.

## 31.5 Findings and exit codes

The report contains `status`, `ready_for_import`, a list of finding codes/severities/messages and metadata-only summary counts. It never includes converted verse text.

- **Exit 0:** no blocking findings; a later, separately reviewed staging transition may be considered.
- **Exit 1:** preflight blocked by one or more blocking findings.
- **Warning:** a documented signature waiver or an explicitly excluded pending cross-edition mapping is visible in the report but does not silently disappear.

A passing preflight is not a publication command. It does not create D1 import rows, approve a human review, change edition availability or publish text.

## 31.6 Run

From the repository root:

```bash
python -m unittest discover -s tests/usfm_preflight -v
```

After a real private import workspace and manifest exist:

```bash
python tools/scripture_import_preflight.py \
  --manifest /private/import-run/preflight-manifest.json \
  --rights-register data/rights/translation-rights-register.json \
  --marker-registry data/usfm/marker-registry.json \
  --proposals-dir data/versification/proposals \
  --output /private/import-run/preflight-report.json
```

The output report is metadata-only. The manifest points to private converted outputs and must not be placed in a public repository if it reveals private object keys or source storage details.

## 31.7 Current project result and remaining gates

The current project data is deliberately not preflight-ready:
- WEBP and KJV rights records remain `review_required`;
- the marker registry is still initial/partial and pending editorial review;
- the Romans 14/16 moved-passage proposal remains pending human review;
- detached archive signature verification has not been completed;
- R2 is not enabled, so private archive/canonical-USX objects cannot yet be verified.

These blockers are expected. The synthetic tests use explicitly synthetic approvals and content only to prove the validator's pass/fail behaviour; they do not modify the real rights register, marker registry or versification decisions.

This implementation does not enable R2, process real WEBP/KJV text, write to D1 or publish Scripture.
