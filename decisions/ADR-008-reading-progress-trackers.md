# ADR-008: Chapter-Based Reading Progress and Independent Trackers

- **Status:** Accepted for product and logical data-model direction; physical migration pending.
- **Date:** 17 November 2026

## Context

The platform needs progress tracking that works with its own reader, a printed Bible or another application. The My Bible Tracker benchmark highlighted chapter completion, multiple independent trackers, clear statistics and a low-pressure experience. The generic user_reading_progress proposal did not adequately express tracker scope, canon selection or guest-local use.

## Decision

1. Model progress through independent reading_trackers.
2. Reference stable scheme_chapters identities, not translation-specific text or verse labels.
3. Give each tracker an explicit canon, versification scheme and whole-canon/selected-book scope.
4. Derive totals, percentages and book states from chapter records.
5. Treat absence of a progress row as unread; allow in_progress and read states.
6. Keep reading-plan completion separate from chapter completion.
7. Support guest-local IndexedDB persistence; a local installation identifier is not authentication.
8. Store cloud trackers under a verified account and enforce ownership server-side.
9. Require explicit, idempotent guest-to-account migration.
10. Defer multi-device sync until conflict and deletion semantics are specified.
11. Keep achievements, reminders and streaks optional and outside the initial core.

## Consequences

Benefits include support for any reading medium, multiple independent goals, stable identity across translation switching, multiple canons, and reliable derived statistics.

Costs include scheme/canon validation, local export and migration work, and more complex future sync. The proposed schema must be validated against actual D1 constraints and Scripture seed data before migration.

## Rejected alternatives

- A generic passage progress row alone: insufficiently expressive for scoped independent trackers.
- Progress tied to translation text: fragments progress when editions change.
- Automatic completion on open/scroll: unreliable and contrary to explicit user intent.
- Mandatory streaks/deadlines: unnecessary pressure.
- Client installation ID as identity: not authentication or proof of ownership.

## Implementation gates

Validate scheme_chapters and canon joins; implement IndexedDB and export; add authenticated endpoints with ownership tests; prove migration idempotency; then enable sync only after conflict semantics are tested.
