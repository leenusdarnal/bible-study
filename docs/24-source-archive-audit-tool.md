# 24. Scripture Source Archive Audit Tool

- **Status:** Implemented as a reproducible metadata-only audit utility; official WEBP/KJV archives successfully scanned in GitHub Actions.
- **Tool:** `tools/scripture_source_audit.py`
- **Workflow:** [Scripture source archive audit](../.github/workflows/scripture-source-audit.yml)
- **Tests:** `tests/source_audit/test_scripture_source_audit.py`
- **Related:** [Source selection](14-scripture-source-selection.md), [Import pipeline](15-dual-bible-text-import-pipeline.md), [Archive audit results](23-source-package-listing-review.md).

## 24.1 Purpose

The tool acquires the declared official eBible.org USFM ZIP archives for WEBP and KJV and produces reproducible archive and primary Scripture-reference metadata without copying verse wording into the reports.

It is an acquisition and structural-audit tool. It is not the final semantic USFM parser, a rights approval system, a versification adjudicator or a D1 import command.

## 24.2 Run tests

From the repository root:

```bash
python -m unittest discover -s tests/source_audit -v
```

The tests use only Python's standard library and create small synthetic ZIP/USFM fixtures. They exercise USFM marker scanning, book IDs, chapter/verse labels, range markers, duplicate labels, core 66-book presence, malformed ZIP handling, path traversal and address comparison.

## 24.3 Download and audit official archives

```bash
python tools/scripture_source_audit.py \
  --download \
  --cache-dir .source-audit-cache \
  --output-dir source-audit-output
```

The utility downloads:
- `https://ebible.org/Scriptures/engwebp_usfm.zip`
- `https://ebible.org/Scriptures/eng-kjv_usfm.zip`

It validates HTTPS response host, response size, ZIP signature, ZIP CRCs, archive/member size limits, duplicate member names, unsafe paths, symlinks and compression ratios. The archives are read in memory; the tool does not extract untrusted member paths to the filesystem. A local content-addressed cache stores the exact downloaded ZIP bytes when `--download` is used.

For a previously downloaded pair of archives:

```bash
python tools/scripture_source_audit.py \
  --source-dir /path/to/source-archives \
  --output-dir source-audit-output
```

The input directory must contain exactly these names:
- `engwebp_usfm.zip`
- `eng-kjv_usfm.zip`

The SHA-256 is calculated over the exact ZIP bytes. The audit compares the download size with the eBible.org directory metadata snapshot recorded in the tool; a mismatch does not automatically reject the package but requires investigation.

## 24.4 Reports

The tool writes:

| File | Contents |
|---|---|
| `audit-manifest.json` | Source URLs, response metadata, hashes, ZIP results, book/chapter/verse totals, marker frequencies and source-to-source address comparison |
| `member-inventory.csv` | Archive member names, compressed/uncompressed sizes, CRCs and USFM hashes/book IDs |
| `book-inventory.csv` | Per-book chapter, verse-marker, unique-address and duplicate-label counts |
| `marker-inventory.csv` | Frequency of USFM markers found in each archive |
| `verse-addresses.csv` | Primary book/chapter/verse labels only; no verse wording |
| `verse-address-differences.csv` | Primary chapter–verse labels that occur in only one source edition |

Reports deliberately omit the Bible verse wording. Exact verse addresses are reference metadata and allow the import team to discover numbering differences before mapping translations.

## 24.5 Safety boundaries and known limitations

- The tool does not copy Bible wording into its metadata reports.
- It does not publish archives or extracted text.
- It does not verify the detached package signature files included in the ZIP; this must be a separately documented integrity check if eBible.org provides the verification procedure.
- The Python ZIP inventory tool performs a structural scan for primary `\\id`, `\\c` and `\\v` lines plus marker-frequency inventory. The separate USFMTC semantic audit described in section 24.8 parses and round-trips the source members.
- It does not detect a USFM version if no `\\usfm` declaration is present.
- It does not establish that two verse labels contain equivalent wording or approve a mapping.
- It does not create Scripture rows, update D1, stage content or publish a translation.
- It does not replace the full semantic parser and source-text round-trip tests described in [15. Dual Bible Text Import and Validation Pipeline](15-dual-bible-text-import-pipeline.md).

## 24.6 GitHub Actions workflow

The workflow:
1. checks out the documentation repository;
2. sets up Python 3.12;
3. runs the source-audit unit tests;
4. downloads and structurally audits both official archives;
5. runs the USFMTC semantic parse and canonical XML round-trip audit over every USFM member;
6. uploads metadata-only structural and semantic reports.

The official binary archives are held only in the GitHub runner's temporary cache for the duration of the job; they are not committed to the repository or uploaded as workflow artifacts. The report artifact is temporary and subject to GitHub retention limits. Archive hashes and key results are preserved in document 23.

The workflow uses Node 24-compatible GitHub actions (`actions/checkout@v7`, `actions/setup-python@v7`, `actions/upload-artifact@v7`).

## 24.7 Current validated run

The final address-comparison run completed successfully on 17 November 2026:

- Workflow run: [44154558855](https://github.com/leenusdarnal/bible-study/actions/runs/44154558855)
- Commit: `31e71250cdde3dbc2446ef65313db950aa6022fd`
- Source audit test suite: 9 passed.
- Both official archive download/CRC/inventory steps: passed.
- Metadata-only report artifact: `scripture-source-audit-44154558855`, artifact ID `14360936095`.

See [23. Source Package Listing Review](23-source-package-listing-review.md) for exact archive SHA-256 hashes, per-edition counts and the Romans address divergence.



## 24.8 Semantic USFM parser diagnostic

The semantic audit uses the **USFM Technical Committee's reference implementation**, the Python package `usfmtc`, pinned to version `0.4.10` (MIT licence). The project describes USFMTC as a reference implementation for reading and writing USFM, USX and USJ. Its documented API reads a USFM file into a USX model, canonicalises it and serialises it back to USFM.

This is preferred over a USFM 3.x-only parser because the eBible source files contain no explicit `\\usfm <version>` declaration. The audit tries the USFM 2.5 profile first and tries 3.1 only for members that do not pass 2.5. A successful profile establishes parser compatibility only; it does not prove which version the publisher authored or declared.

For each member, the diagnostic:
1. reads the source file under each candidate profile;
2. canonicalises the parsed USX representation;
3. serialises it back to USFM;
4. reparses the generated USFM;
5. compares full canonical XML fingerprints, including text, while writing only hashes and structural metadata to the report.

The report contains no Scripture wording. It records source hashes, parser profile results, parse error counts, round-trip status and structural element counts. The source text is held only in the ephemeral runner process.

The GitHub Actions workflow installs the pinned USFMTC version, safely extracts only validated USFM members into the ephemeral runner workspace and executes this audit over both editions. The original ZIP archives and extracted Scripture files are not committed or uploaded. Only metadata-only reports are retained as workflow artifacts.

- Reference implementation: [usfm-bible/usfmtc](https://github.com/usfm-bible/usfmtc)
- Diagnostic workflow: [USFMTC-based run 44250112893](https://github.com/leenusdarnal/bible-study/actions/runs/44250112893) (completed successfully; see section 24.9)
- Acceptance condition: every source member must parse and round-trip under the first successful candidate profile with an identical canonical XML fingerprint. The profile is recorded as a compatibility profile, never as a publisher-declared source version.
- A successful round-trip is a strong structural/text preservation check, not a substitute for manual review of marker semantics, versification exceptions or legal publication rights.


## 24.9 Semantic audit result — 18 November 2026

The pinned USFMTC parser successfully parsed and round-tripped all 149 source USFM members:

| Source | Files | Passed | Review required | 3.1 fallback |
|---|---:|---:|---:|---:|
| WEBP | 68 | 68 | 0 | 0 |
| KJV | 81 | 81 | 0 | 0 |
| **Total** | **149** | **149** | **0** | **0** |

Every member passed under the first USFM 2.5 compatibility profile. This is not a claim that the publisher declared USFM 2.5; the source files contain no explicit version marker.

- Workflow: [44250112893](https://github.com/leenusdarnal/bible-study/actions/runs/44250112893)
- Commit: `89494243ee8c0db99c25a5090a5d74aec541f59b`
- Parser: `usfmtc 0.4.10`
- Metadata-only artifact: `scripture-source-audit-44250112893`, artifact ID `14403203746`
- Artifact SHA-256: `823c0975de780d602ec23a8bcc3824b502143aaaffa8195237a0bdf8f466606e`

The result closes initial source parsing and canonical XML round-trip validation for these exact archive checksums. It does not close source-signature verification, marker interpretation review, verse mapping approval, territorial rights clearance or D1 publication.


## 24.10 Semantic marker-style inventory

The semantic audit report now aggregates USX element counts and USX `style` attribute values by source edition, in addition to per-file counts. These values provide a concrete inventory of structural elements and marker styles that the importer must handle or explicitly retain as unknown nodes.

The inventory is metadata only: it contains marker/style identifiers and counts, not Scripture wording. It is a discovery input for the versioned marker registry, not a claim that every marker's semantics have already been reviewed. The report schema is version 2.

The summary helper has a regression test confirming that element/style counts are retained while verse and note wording is excluded from the summary output.
