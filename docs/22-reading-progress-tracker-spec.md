# 22. Reading Progress Tracker Specification

- **Status:** Proposed; ready for implementation planning.
- **Benchmark:** [My Bible Tracker](21-product-reference-my-bible-tracker.md).
- **Related:** [Product experience](02-product-experience.md), [Data model](04-data-model.md), [Database schema](11-database-schema.md).
- **Purpose:** Track reading whether a person uses this platform, a printed Bible or another app.

## 22.1 Principles

1. Chapter-level completion, independent of translation text and reader sessions.
2. Explicit canon and book scope; never silently assume every user follows the Protestant 66-book canon.
3. Flexible, non-linear reading and editable past progress.
4. Private by default, accessible without relying on colour alone.
5. Low pressure: no mandatory streaks, deadlines, overdue labels or punitive reminders.
6. Reading plans and chapter completion are separate concepts.
7. Guest use must not require registration.

## 22.2 User stories

- A guest can create a tracker and retain it on the same device/browser.
- A reader can track an entire canon or a selected set of books.
- A reader can mark any chapter read or unread without opening its text.
- A reader can see chapter, book and overall progress with a clear denominator.
- A reader can resume recent activity or choose any unread chapter.
- A reader can keep multiple independent trackers.
- An account holder can export, delete and eventually sync private progress.
- A reader can use progress tracking with a printed Bible.

## 22.3 Priorities

| Priority | Capability | Timing |
|---|---|---|
| P0 | Create tracker, choose canon and whole/selected-book scope | Initial |
| P0 | Mark/unmark chapter; mark/reset whole book | Initial |
| P0 | Derived book states, totals, percentage and resume suggestion | Initial |
| P0 | Guest-local persistence and private account storage | Initial |
| P1 | Multiple trackers, names, descriptions and colour tokens | Initial foundation |
| P1 | Per-book statistics and export/import | Initial / before broad adoption |
| P2 | Achievements and milestones | Later |
| P2 | Optional reading-plan linkage and reminders | Later |
| P2 | Multi-device sync and conflict resolution | Later |

## 22.4 Tracker configuration

Each tracker has a name, optional description, canon, versification scheme, scope mode (all books or selected books), optional accessible colour token, timestamps and optional archive timestamp. Selected-book scope must contain at least one book, and every selected book must belong to the chosen canon. The SQL migration requires selected scope to be activated within a transaction: insert the tracker initially as all-books, add at least one selected-book row, then change the scope to selected-books before committing. This also makes scope changes auditable and prevents an empty selected scope from being committed.

Changing canon or scope after progress exists requires a preview of which chapters remain in scope. Do not silently delete excluded progress. To change from all-books to selected-books, the service adds one or more selected-book rows and activates selected scope in one transaction. The SQL migration prevents committing a selected scope with no books and prevents removing or moving its final selected book. When replacing the last book, add the replacement first or switch to all-books within the same transaction.

## 22.5 Chapter states and interactions

- Unread: no progress row exists.
- In progress: user has started the chapter but has not completed it.
- Read: user explicitly marked it complete.

The first interface may expose only a read/unread toggle; the schema supports in-progress for later. Opening, scrolling or spending time in a chapter must never automatically mark it read.

Users can mark any chapter read/unread, mark all chapters in a book read, or reset a book with confirmation/undo. Non-linear completion is supported.

## 22.6 Statistics

Derive all statistics from tracker scope, canon membership, scheme chapters and progress rows. Do not store counters that can drift.

- Total chapters: count of chapters in the tracker's selected canon and book scope.
- Chapters read: count of in-scope chapters with read state.
- Percentage: chapters read divided by total chapters, multiplied by 100.
- Books complete: every in-scope chapter is read.
- Books in progress: at least one chapter is read/in-progress and at least one is not read.
- Books untouched: no progress record exists for that book.
- Last activity: most recent progress mutation.
- Resume suggestion: most recently interacted in-scope chapter; otherwise the first unread chapter in canon/book order.

Show the denominator and canon, e.g. “42 of 1,189 chapters in the Protestant 66-book canon”. Never hard-code the denominator. Selected-book trackers use only selected books.

## 22.7 Data model

Use stable Scripture chapter identities, not translation-specific verse IDs or printed labels.

### reading_trackers
id PK; user_id FK for cloud records; name; description; canon_id FK; versification_scheme_id FK; scope_mode; colour_token; created_at; updated_at; archived_at.

### reading_tracker_books
id PK; tracker_id FK; canon_id FK; work_id FK; display_order; UNIQUE(tracker_id, work_id). Used for selected-book scope. The selection list may be retained while all-books scope is active; it affects statistics only when selected-books scope is active.

### reading_tracker_chapter_progress
id PK; tracker_id FK; canon_id FK; versification_scheme_id FK; work_id FK; chapter_id FK to scheme_chapters; progress_state (in_progress or read); started_at; completed_at; updated_at; UNIQUE(tracker_id, chapter_id).

No row means unread. A read state requires completed_at; other states must not have a completion timestamp. Composite foreign keys bind the tracker to its canon and scheme and bind each chapter row to its scheme, work and canon. Triggers reject progress outside the active selected-book scope, re-check edits to historical out-of-scope rows, require selected scope to be activated only after adding a selection, and prevent removing or moving the last selected book. The service must still validate ownership and the current scope.

An optional event/history table and achievements tables are deferred. Do not build them into the first migration without a demonstrated need.

## 22.8 Guests, accounts and sync

**Guest mode:** store trackers and progress in IndexedDB. Explain that guest data is local to the browser/device. Use the same domain model and validation as account records. A client-generated installation ID is not authentication. Provide export/backup before users rely on local-only data.

**Signed-in mode:** cloud trackers belong to a verified account. Every read/write/export/delete operation enforces ownership on the server. Never trust a user_id supplied by the client as proof of ownership.

**Migration:** require explicit consent; use stable IDs and idempotent upserts; validate canon, scope and chapter identities; show a migration summary; retain a local backup until success is confirmed. If a similar tracker exists, offer merge or keep separate rather than silently combining.

**Multi-device sync:** later phase. Define client mutation IDs, revisions, deletion tombstones and deterministic conflict rules first. Do not promise background sync until tested; sync on app open/reconnect is an acceptable baseline.

## 22.9 Reading plans are separate

A plan defines suggested passages and schedule; a tracker records what a person says they have read. Completing a plan day does not automatically mark chapters read, and marking a chapter read does not complete a plan day. Plan deadlines and reminders never alter tracker records.

## 22.10 Privacy and accessibility

Keep personal progress private. Collect only data needed for operation and sync. Provide export and deletion. Explain local versus cloud storage accurately. Do not use reading history for advertising or unnecessary profiling.

Never rely on colour alone. Provide accessible labels such as “Genesis, chapter 1, read”; visible focus; large touch targets; keyboard and screen-reader support. Test narrow Android screens, enlarged text, device insets, bottom navigation and the final row of chapter controls.

## 22.11 Acceptance criteria

1. Guest creates a tracker, closes and reopens the same browser, and retains progress.
2. Any chapter can be marked read and reversed without opening Scripture text.
3. Whole-book mark/reset updates all applicable chapter states.
4. Totals and percentages are derived from the selected scope.
5. Selected-book trackers exclude other books from the denominator.
6. Different canons produce their own book/chapter totals.
7. Two trackers can record different states for the same chapter.
8. Tracker use does not require a reading plan.
9. Server rejects attempts to access another user's tracker.
10. Guest migration is retry-safe and does not create duplicates.
11. Mobile chapter controls remain visible and usable with enlarged text.
12. No streak, reminder or deadline is mandatory.
13. Export includes scope and stable chapter identities for validated re-import.

## 22.12 Tests and implementation gates

Unit tests: percentage, denominator, book-state derivation, selected-book validation, whole-book operations and resume selection.

Integration tests: overlapping trackers, ownership, migration idempotency, scope changes, plan independence, D1 constraints and foreign keys.

End-to-end tests: printed-Bible workflow, marking from tracker without opening text, reader's explicit mark action, small mobile viewport, keyboard and screen-reader labels.

Before production: validate scheme_chapters keys and canon joins; implement IndexedDB and export; prove auth compatibility; test D1 migrations and ownership; define account deletion/backup retention; and specify sync conflict rules.

## 22.13 Decision summary

Adopt chapter-based progress as a first-release capability. Model independent trackers against stable Scripture chapter identities and explicit canon/scope. Support guest-local persistence and private account storage. Defer achievements, advanced reminders and multi-device sync until their privacy and conflict behaviour are tested.


## 22.14 Validation status

The draft migrations and tracker regression tests pass in SQLite. GitHub Actions also applies migrations 0001–0003 to a fresh Wrangler local D1 database, verifies the Protestant canon seed contains 66 included books and checks that no foreign-key violations are reported (run [44249782265](https://github.com/leenusdarnal/bible-study/actions/runs/44249782265)).

The same local D1 CI run also confirms that a selected-books tracker can be assembled transactionally, valid Genesis progress is accepted, progress for an unselected Exodus chapter is rejected, the last selected book cannot be deleted and an empty selected-books tracker cannot be inserted directly (run [44250072396](https://github.com/leenusdarnal/bible-study/actions/runs/44250072396)). This does **not** yet validate every trigger edge case under D1, authentication ownership, IndexedDB guest storage, sync or account deletion. Those remain pre-production tasks.
