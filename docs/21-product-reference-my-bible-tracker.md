# Product Reference: My Bible Tracker

**Status:** Adopted as a focused product-design reference for reading progress  
**Reviewed:** 17 November 2026  
**Project:** Bible Study Repo

## 1. Product overview

My Bible Tracker is an Android/iOS companion app designed to track Bible reading progress while a person reads from their own preferred Bible. It is deliberately not positioned as a full Bible text reader or commentary platform.

- Google Play: https://play.google.com/store/apps/details?id=com.biblereadingprogresstracker.BibleTracker
- Developer website: https://mybibletracker.com/
- Privacy policy: https://stinejohanne.github.io/BibleTrackerPrivacyPolicy.io/

At the time of review, the Google Play listing showed:
- 100K+ downloads.
- 4.1-star rating and approximately 880 reviews (the page also displayed a separate 4.0 rating/842-review count in its review section).
- Last updated 12 September 2026.
- Languages listed on Google Play included English, Spanish, French, German, Portuguese, Italian, Dutch, Russian, Chinese, Thai, Hungarian, Ukrainian, Hindi, Belarusian, Norwegian, Swedish and Danish.

Store metrics are time-sensitive and are recorded as observed on the review date, not as enduring product facts.

## 2. Core features observed

The official Google Play listing and developer website describe:

- Mark individual Bible chapters as read.
- Mark an entire book as read.
- Visual indication of completed books and partially completed books.
- Multiple independent trackers for different reading purposes.
- Custom tracker names and colours.
- Percentage of the Bible read.
- Statistics for chapters and books completed.
- Achievements as progress milestones.
- No forced timed plan or daily checklist.
- No annoying notifications, according to the developer's product description.
- Multilingual interface.

The app is designed to work alongside a user's preferred physical or digital Bible. Its focus is progress tracking, not supplying the Scripture text itself.

## 3. What user feedback suggests

The Google Play listing includes positive user comments about:
- Simple chapter-by-chapter check-off.
- Seeing overall progress and completion percentage.
- Reading at an individual pace without time pressure.
- Running multiple trackers for different studies or Bibles.
- Quickly identifying where reading has stopped.

The listing also includes a usability complaint about controls at the bottom of a screen being obstructed by a toolbar. This is a useful reminder to test scrolling, safe areas, touch targets and small-screen layouts.

These are selected store comments, not a representative or statistically rigorous user study.

## 4. Lessons for Bible Study Repo

### 4.1 Progress tracking should be a first-class feature

A user may want to track progress even when reading a printed Bible or another app.

**Requirement:** offer a dedicated progress tracker that is independent of the built-in reader. Users should be able to mark a chapter complete without opening the Scripture text in our platform.

### 4.2 Support multiple independent trackers

Different reading goals may run in parallel: a whole-Bible journey, New Testament reading, Psalms, a study group plan or a particular translation.

**Requirement:** users can create multiple trackers with a title, colour, canon/book scope, optional description and independent progress. Trackers must not overwrite each other.

### 4.3 Provide chapter-level completion

Book-level completion alone is too coarse for real reading habits.

**Requirement:** show each book's chapter grid/list with clear states: unread, read and optionally in progress. Permit non-linear reading and editing past completion states.

### 4.4 Make progress understandable at a glance

A single percentage is motivating but insufficient for detailed planning.

**Requirement:** show overall completion, books completed, chapters completed, per-book progress and a clear resume/next-unread suggestion. State the denominator and canon used in every percentage.

### 4.5 Avoid guilt-driven engagement

The app's no-deadline approach is a strong design lesson. Reading habits vary and missed days should not erase progress or create shame.

**Requirement:** no mandatory streaks, punitive reminders or overdue labels. Reading plans and notifications must be optional. Achievements should encourage rather than pressure.

### 4.6 Support flexible milestones

Achievements can make long-term reading progress visible.

**Requirement:** optional milestones such as first chapter, first book, first 10 books, New Testament completed and whole selected canon completed. Keep milestone definitions transparent and avoid turning spiritual practice into competition.

### 4.7 Make accessibility and responsive testing mandatory

The bottom-toolbar complaint highlights a common mobile usability failure.

**Requirement:** test chapter controls on small Android screens, larger font settings, screen readers, keyboard navigation, device insets, bottom navigation overlays and scrolling to the final item.

## 5. Proposed feature requirements

| Priority | Feature | Requirement |
|---|---|---|
| P0 | Basic progress | Mark/unmark a chapter read |
| P0 | Book progress | Derive completed and partially completed book states |
| P0 | Whole-canon statistics | Calculate chapter and book percentages using a clearly selected canon |
| P1 | Multiple trackers | Independent tracker definitions and progress |
| P1 | Customisation | Tracker name, colour and optional description |
| P1 | Resume | Identify last activity and next unread chapter |
| P1 | Flexible order | Allow reading and marking chapters in any order |
| P2 | Achievements | Optional, non-punitive milestones |
| P2 | Reading plans | Link tracker progress to structured plan steps, without conflating the two |
| P2 | Import/export | Allow personal progress backup and portable export |

## 6. Data model implications

The existing Scripture core provides the canonical book and chapter identities. Add a separate personal progress model rather than storing progress on the Bible text itself.

Suggested conceptual entities:

- `reading_trackers`: owner/guest scope, name, colour, description, canon, created and updated timestamps.
- `reading_tracker_books`: optional scope/order overrides if a tracker covers only selected books.
- `reading_tracker_chapter_progress`: tracker, stable book/chapter identity, status, completed timestamp, updated timestamp.
- `reading_tracker_events`: optional history for undo, audit and statistics.
- `reading_achievements`: achievement definitions and version.
- `user_achievements`: private earned milestone records.

Important rules:
- Track progress against stable Scripture chapter identities, not a translation's displayed verse labels.
- A tracker must specify its canon/book scope. Do not assume all users use the Protestant 66-book canon.
- Completion percentage = completed chapters divided by total chapters in that tracker's selected scope.
- A partially read book is derived from chapter states, not a separately maintained counter.
- Reading tracker progress is private personal data.
- Guest progress should persist locally and have a clear migration path if the user later creates an account.
- Multiple devices require conflict handling; local-only progress and cloud-synced progress must be clearly distinguished.

## 7. Privacy and security notes

The developer's published privacy policy says user-entered data is stored locally on the device and that the app does not collect or store personally identifiable information. It also identifies Google Play Services as a third-party service.

Google Play's data-safety section is developer-provided and may change. At review time, the listing indicated no data collected or shared and displayed a statement that data is not encrypted. These store disclosures should not be treated as an independent security audit.

For Bible Study Repo:
- Keep personal reading history and notes private by default.
- Document local storage and cloud sync accurately.
- Encrypt account data in transit and at rest where applicable.
- Provide export and deletion controls.
- Avoid analytics that collect unnecessary personal reading behaviour.
- Publish a clear privacy policy consistent with actual implementation.

## 8. Recommended placement in Bible Study Repo

Add a **Reading Progress** area under Home and My Library, and expose a small progress indicator in the Bible reader.

Suggested user experience:
1. Create a tracker (e.g. “Read the Whole Bible”).
2. Select a canon or a set of books.
3. See all books with chapter completion indicators.
4. Tap chapters to mark them read or unread.
5. View overall and per-book progress.
6. Resume from the last activity or choose any unread chapter.
7. Create another independent tracker if desired.

The tracker must work even if the user reads from a printed Bible or another app.

## 9. What not to copy

- Do not copy the app's name, logo, screenshots, exact visual design or proprietary assets.
- Use the feature concepts as inspiration and implement an original interface.
- Do not assume the app's local storage model is appropriate for a multi-device web platform.
- Do not introduce streak pressure or notifications that contradict the low-pressure reading approach.

## 10. Decision

My Bible Tracker is adopted as a **benchmark for chapter-level reading progress, multiple independent trackers, at-a-glance statistics and low-pressure motivation**.

The Reading Progress feature should be included in the initial platform foundation, with multiple trackers and achievements phased after the basic chapter progress model. It should be available independently of the platform's own Bible reader.
