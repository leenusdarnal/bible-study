# ADR-003: Content Governance and Evidence

- **Status:** Accepted.
- **Date:** 2026-11-16

## Context

The platform combines Scripture, historical research, scholarship, theological interpretation, third-party datasets and community submissions. Incorrect or unlicensed material could undermine trust.

## Decision

Use staging -> validation -> reconciliation -> specialist/editorial review -> publication. Automated duplicate detection may propose matches, but uncertain merges require human approval. Every sourced record retains attribution, licence, source version and retrieval metadata. Community submissions remain unverified until approved. AI-generated content, when introduced, remains draft-only until editorial review.

## Consequences

- Public content is traceable and auditable.
- Import and publication are slower than direct ingestion but safer.
- Review states and revision history must be represented in the data model.
- Rights checks are required separately for display, caching, transformation and AI use.
