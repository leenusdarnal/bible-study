# 28. Translation Rights Register and Publication Gate

- **Status:** Initial machine-readable register and fail-closed validator implemented; WEBP and KJV remain unapproved.
- **Date:** 18 November 2026
- **Related:** [Licensing and attribution](09-licensing-attribution.md), [Import staging and publication](27-scripture-import-staging-and-publication.md).

## 28.1 Purpose

The register separates source acquisition from permission to publish. A successful download, public source URL, parser round-trip or public-domain statement in one country does not establish worldwide permission to redistribute a complete digital translation.

## 28.2 Implemented files

- `data/rights/translation-rights-register.json` — per-edition source, evidence, territory, permissions and review status.
- `tools/validate_translation_rights.py` — standard-library validator and publication gate.
- `tests/rights/test_validate_translation_rights.py` — regression tests.

## 28.3 Fail-closed rules

An edition can pass a territory-specific publication check only when:
1. `rights_status` is `approved`;
2. the requested territory is explicitly listed;
3. display and caching permissions are explicitly true;
4. supporting evidence is recorded;
5. a named reviewer, review date and decision reference are present.

Redistribution, transformation and AI-use permissions are separate fields. They are not inferred from display permission. Conditional and unknown permissions never count as approval.

## 28.4 Run

```bash
python -m unittest discover -s tests/rights -v
python tools/validate_translation_rights.py data/rights/translation-rights-register.json
python tools/validate_translation_rights.py data/rights/translation-rights-register.json --territory IN
```

The initial WEBP and KJV records are deliberately marked `review_required`, with no approved territories and unknown permissions. This is not a legal determination. It is a safe representation of the current evidence gap. The validator is a policy gate, not legal advice or a substitute for review of the exact edition, rights holder, licence and intended uses.

## 28.5 Current boundary

This implementation does not change D1, enable R2, import Bible text or publish either translation. It can be completed and tested independently while cloud storage work is deferred.
