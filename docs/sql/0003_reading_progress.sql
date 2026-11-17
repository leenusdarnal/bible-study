-- DRAFT ONLY. Requires 0001 Scripture core and canon seed.
-- Cloud account-owned records only; guest trackers remain in IndexedDB.
-- Auth-provider FK is deferred until the auth provider is selected.

CREATE TABLE reading_trackers (
  id TEXT PRIMARY KEY NOT NULL,
  user_id TEXT NOT NULL,
  name TEXT NOT NULL CHECK (length(trim(name)) > 0),
  description TEXT,
  canon_id TEXT NOT NULL,
  versification_scheme_id TEXT NOT NULL,
  scope_mode TEXT NOT NULL CHECK (scope_mode IN ('all_books', 'selected_books')),
  colour_token TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  archived_at INTEGER,
  FOREIGN KEY (canon_id) REFERENCES canons(id) ON DELETE RESTRICT,
  FOREIGN KEY (versification_scheme_id) REFERENCES versification_schemes(id) ON DELETE RESTRICT,
  UNIQUE (id, canon_id),
  UNIQUE (id, versification_scheme_id)
);

CREATE TABLE reading_tracker_books (
  id TEXT PRIMARY KEY NOT NULL,
  tracker_id TEXT NOT NULL,
  canon_id TEXT NOT NULL,
  work_id TEXT NOT NULL,
  display_order INTEGER NOT NULL CHECK (display_order > 0),
  FOREIGN KEY (tracker_id, canon_id) REFERENCES reading_trackers(id, canon_id) ON DELETE CASCADE,
  FOREIGN KEY (canon_id, work_id) REFERENCES canon_books(canon_id, work_id) ON DELETE RESTRICT,
  UNIQUE (tracker_id, work_id),
  UNIQUE (tracker_id, display_order)
);

CREATE TABLE reading_tracker_chapter_progress (
  id TEXT PRIMARY KEY NOT NULL,
  tracker_id TEXT NOT NULL,
  canon_id TEXT NOT NULL,
  versification_scheme_id TEXT NOT NULL,
  work_id TEXT NOT NULL,
  chapter_id TEXT NOT NULL,
  progress_state TEXT NOT NULL CHECK (progress_state IN ('in_progress', 'read')),
  started_at INTEGER NOT NULL,
  completed_at INTEGER,
  updated_at INTEGER NOT NULL,
  FOREIGN KEY (tracker_id, canon_id) REFERENCES reading_trackers(id, canon_id) ON DELETE CASCADE,
  FOREIGN KEY (tracker_id, versification_scheme_id) REFERENCES reading_trackers(id, versification_scheme_id) ON DELETE CASCADE,
  FOREIGN KEY (chapter_id, versification_scheme_id, work_id)
    REFERENCES scheme_chapters(id, scheme_id, work_id) ON DELETE RESTRICT,
  FOREIGN KEY (canon_id, work_id) REFERENCES canon_books(canon_id, work_id) ON DELETE RESTRICT,
  UNIQUE (tracker_id, chapter_id),
  CHECK (
    (progress_state = 'read' AND completed_at IS NOT NULL)
    OR (progress_state = 'in_progress' AND completed_at IS NULL)
  )
);

CREATE INDEX idx_reading_trackers_owner_updated ON reading_trackers(user_id, updated_at DESC);
CREATE INDEX idx_reading_tracker_books_tracker_order ON reading_tracker_books(tracker_id, display_order);
CREATE INDEX idx_reading_tracker_progress_tracker_state ON reading_tracker_chapter_progress(tracker_id, progress_state);
CREATE INDEX idx_reading_tracker_progress_chapter ON reading_tracker_chapter_progress(chapter_id, tracker_id);

CREATE TRIGGER trg_tracker_progress_selected_scope_insert
BEFORE INSERT ON reading_tracker_chapter_progress
WHEN (SELECT scope_mode FROM reading_trackers WHERE id = NEW.tracker_id) = 'selected_books'
AND NOT EXISTS (
  SELECT 1 FROM reading_tracker_books b
  WHERE b.tracker_id = NEW.tracker_id AND b.canon_id = NEW.canon_id AND b.work_id = NEW.work_id
)
BEGIN
  SELECT RAISE(ABORT, 'chapter is outside selected tracker book scope');
END;

CREATE TRIGGER trg_tracker_progress_selected_scope_update
BEFORE UPDATE OF tracker_id, canon_id, work_id, chapter_id, progress_state, started_at, completed_at, updated_at ON reading_tracker_chapter_progress
WHEN (SELECT scope_mode FROM reading_trackers WHERE id = NEW.tracker_id) = 'selected_books'
AND NOT EXISTS (
  SELECT 1 FROM reading_tracker_books b
  WHERE b.tracker_id = NEW.tracker_id AND b.canon_id = NEW.canon_id AND b.work_id = NEW.work_id
)
BEGIN
  SELECT RAISE(ABORT, 'chapter is outside selected tracker book scope');
END;

-- Selected-book scope is activated by a transactional sequence:
-- create tracker as all_books, insert one or more selected-book rows,
-- then update scope_mode to selected_books. This avoids committing an empty selection.

CREATE TRIGGER trg_tracker_selected_scope_insert_requires_selection
BEFORE INSERT ON reading_trackers
WHEN NEW.scope_mode = 'selected_books'
BEGIN
  SELECT RAISE(ABORT, 'create selected scope by adding books before activating selected_books');
END;

CREATE TRIGGER trg_tracker_books_prevent_empty_selected_scope
BEFORE DELETE ON reading_tracker_books
WHEN (SELECT scope_mode FROM reading_trackers WHERE id = OLD.tracker_id) = 'selected_books'
AND (SELECT COUNT(*) FROM reading_tracker_books WHERE tracker_id = OLD.tracker_id) = 1
BEGIN
  SELECT RAISE(ABORT, 'selected_books scope must retain at least one selected book');
END;

CREATE TRIGGER trg_tracker_books_prevent_moving_last_selected_book
BEFORE UPDATE OF tracker_id, canon_id ON reading_tracker_books
WHEN (OLD.tracker_id <> NEW.tracker_id OR OLD.canon_id <> NEW.canon_id)
AND (SELECT scope_mode FROM reading_trackers WHERE id = OLD.tracker_id) = 'selected_books'
AND (SELECT COUNT(*) FROM reading_tracker_books WHERE tracker_id = OLD.tracker_id) = 1
BEGIN
  SELECT RAISE(ABORT, 'selected_books scope must retain at least one selected book');
END;

CREATE TRIGGER trg_tracker_books_scope_requires_selection
BEFORE UPDATE OF scope_mode ON reading_trackers
WHEN NEW.scope_mode = 'selected_books'
AND NOT EXISTS (SELECT 1 FROM reading_tracker_books b WHERE b.tracker_id = NEW.id)
BEGIN
  SELECT RAISE(ABORT, 'selected_books scope requires at least one selected book');
END;


-- Create a selected-books tracker and its first selected book in one transaction.
-- Excluded historical progress is retained but excluded from current calculations.
