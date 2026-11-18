# Architecture Decision Records

This directory records decisions that materially shape the Bible Study Repo. Statuses are evidence-based and should be updated when implementation or validation changes.

| ADR | Decision | Current status |
|---|---|---|
| [ADR-001](ADR-001-technology-stack.md) | Technology stack | Recorded; revalidate versions before implementation |
| [ADR-002](ADR-002-data-architecture.md) | Data architecture | Recorded |
| [ADR-003](ADR-003-content-governance.md) | Content and research governance | Recorded |
| [ADR-004](ADR-004-first-release-scope.md) | First-release scope | Recorded |
| [ADR-005](ADR-005-database-schema.md) | Database schema | Recorded; implementation validation remains ongoing |
| [ADR-006](ADR-006-scripture-core-schema.md) | Scripture core schema | Proposed; fresh local D1 migrations and integrity checks pass; behavioural and Drizzle validation remain open |
| [ADR-007](ADR-007-dual-bible-text-corpus.md) | Dual Bible text corpus and lossless USFM import | Proposed; source acquisition, structural audit and 149-file semantic round-trip complete; versification and rights gates remain open |
| [ADR-008](ADR-008-reading-progress-trackers.md) | Reading progress trackers | Proposed; SQLite regression and local D1 migration/selected-scope trigger checks pass; preview/auth/sync validation remains open |
| [ADR-009](ADR-009-dual-edition-scripture-import.md) | Dual-edition Scripture import implementation | Proposed; semantic parsing complete; mapping approval and legal review remain open |

## Change control

- Use the next unused ADR number; never reuse an existing number.
- Keep one decision per ADR where practical. Link related decisions instead of duplicating the same decision under two numbers.
- Use the statuses Proposed, Accepted, Superseded or Rejected consistently.
- Do not mark a decision Accepted merely because code or documentation exists; required validation and approval gates must be met.
- When replacing an ADR, preserve the old record and mark it Superseded, or explicitly document the consolidation and retain a clear link to the replacement.
