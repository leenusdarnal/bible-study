-- DRAFT ONLY. Requires migrations 0001_scripture_core.sql and 0005_translation_text_content_states.sql.
-- Import-run provenance, source-file inventory, private staging units and validation evidence.
-- This migration creates no Bible text records in the published Scripture tables.

CREATE TABLE scripture_import_runs (
  id TEXT PRIMARY KEY NOT NULL,
  edition_id TEXT NOT NULL,
  versification_scheme_id TEXT NOT NULL,
  source_archive_url TEXT NOT NULL,
  source_archive_object_key TEXT NOT NULL,
  source_archive_sha256 TEXT NOT NULL
    CHECK (
      length(source_archive_sha256) = 64
      AND source_archive_sha256 NOT GLOB '*[^0-9a-f]*'
    ),
  source_archive_size_bytes INTEGER NOT NULL CHECK (source_archive_size_bytes > 0),
  source_retrieved_at INTEGER NOT NULL,
  parser_name TEXT NOT NULL,
  parser_version TEXT NOT NULL,
  parser_compatibility_profile TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'acquired'
    CHECK (status IN (
      'acquired', 'inventoried', 'parsed', 'validated',
      'reviewed', 'published', 'failed', 'rejected'
    )),
  manifest_json TEXT NOT NULL CHECK (json_valid(manifest_json)),
  validation_summary_json TEXT
    CHECK (validation_summary_json IS NULL OR json_valid(validation_summary_json)),
  approved_by TEXT,
  approval_reference TEXT,
  approved_at INTEGER,
  published_at INTEGER,
  failure_code TEXT,
  failure_summary TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  FOREIGN KEY (edition_id, versification_scheme_id)
    REFERENCES translation_editions(id, versification_scheme_id) ON DELETE RESTRICT,
  UNIQUE (
    edition_id, source_archive_sha256, parser_name,
    parser_version, parser_compatibility_profile
  ),
  UNIQUE (id, edition_id, versification_scheme_id),
  UNIQUE (id, versification_scheme_id),
  CHECK (
    status NOT IN ('reviewed', 'published')
    OR (approved_by IS NOT NULL AND approved_at IS NOT NULL)
  ),
  CHECK (status <> 'published' OR published_at IS NOT NULL)
);

CREATE TABLE scripture_import_files (
  id TEXT PRIMARY KEY NOT NULL,
  import_run_id TEXT NOT NULL,
  member_name TEXT NOT NULL,
  member_sha256 TEXT NOT NULL
    CHECK (
      length(member_sha256) = 64
      AND member_sha256 NOT GLOB '*[^0-9a-f]*'
    ),
  member_size_bytes INTEGER NOT NULL CHECK (member_size_bytes >= 0),
  book_code TEXT,
  work_id TEXT,
  parse_status TEXT NOT NULL DEFAULT 'discovered'
    CHECK (parse_status IN ('discovered', 'parsed', 'review_required', 'rejected', 'skipped')),
  declared_usfm_version TEXT,
  parser_compatibility_profile TEXT,
  canonical_usx_object_key TEXT,
  canonical_usx_sha256 TEXT
    CHECK (
      canonical_usx_sha256 IS NULL
      OR (
        length(canonical_usx_sha256) = 64
        AND canonical_usx_sha256 NOT GLOB '*[^0-9a-f]*'
      )
    ),
  chapter_count INTEGER CHECK (chapter_count IS NULL OR chapter_count >= 0),
  verse_marker_count INTEGER CHECK (verse_marker_count IS NULL OR verse_marker_count >= 0),
  warning_count INTEGER NOT NULL DEFAULT 0 CHECK (warning_count >= 0),
  error_count INTEGER NOT NULL DEFAULT 0 CHECK (error_count >= 0),
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  FOREIGN KEY (import_run_id) REFERENCES scripture_import_runs(id) ON DELETE RESTRICT,
  FOREIGN KEY (work_id) REFERENCES scriptural_works(id) ON DELETE RESTRICT,
  UNIQUE (import_run_id, member_name),
  UNIQUE (import_run_id, id)
);

CREATE TABLE scripture_import_staging_units (
  id TEXT PRIMARY KEY NOT NULL,
  import_run_id TEXT NOT NULL,
  source_file_id TEXT NOT NULL,
  versification_scheme_id TEXT NOT NULL,
  work_id TEXT NOT NULL,
  source_chapter_label TEXT NOT NULL,
  source_chapter_order INTEGER NOT NULL CHECK (source_chapter_order > 0),
  source_unit_label TEXT NOT NULL,
  source_unit_order INTEGER NOT NULL CHECK (source_unit_order > 0),
  source_marker_order INTEGER NOT NULL CHECK (source_marker_order >= 0),
  unit_kind TEXT NOT NULL DEFAULT 'verse'
    CHECK (unit_kind IN ('verse', 'heading', 'superscription', 'other')),
  content_state TEXT NOT NULL DEFAULT 'text'
    CHECK (content_state IN ('text', 'annotation_only', 'empty_marker')),
  text TEXT NOT NULL DEFAULT '',
  footnote_metadata_json TEXT
    CHECK (footnote_metadata_json IS NULL OR json_valid(footnote_metadata_json)),
  structured_content_json TEXT
    CHECK (structured_content_json IS NULL OR json_valid(structured_content_json)),
  validation_status TEXT NOT NULL DEFAULT 'pending'
    CHECK (validation_status IN ('pending', 'valid', 'review_required', 'rejected')),
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  FOREIGN KEY (import_run_id, versification_scheme_id)
    REFERENCES scripture_import_runs(id, versification_scheme_id) ON DELETE RESTRICT,
  FOREIGN KEY (import_run_id, source_file_id)
    REFERENCES scripture_import_files(import_run_id, id) ON DELETE RESTRICT,
  FOREIGN KEY (work_id) REFERENCES scriptural_works(id) ON DELETE RESTRICT,
  UNIQUE (import_run_id, work_id, source_chapter_label, source_unit_label),
  UNIQUE (import_run_id, source_file_id, source_marker_order),
  CHECK (
    (content_state = 'text' AND length(trim(text)) > 0)
    OR (
      content_state = 'annotation_only'
      AND length(trim(text)) = 0
      AND footnote_metadata_json IS NOT NULL
    )
    OR (
      content_state = 'empty_marker'
      AND length(trim(text)) = 0
      AND footnote_metadata_json IS NULL
    )
  )
);

CREATE TABLE scripture_import_validation_results (
  id TEXT PRIMARY KEY NOT NULL,
  import_run_id TEXT NOT NULL,
  source_file_id TEXT,
  rule_code TEXT NOT NULL,
  severity TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'error', 'blocking')),
  result TEXT NOT NULL CHECK (result IN ('passed', 'failed', 'skipped')),
  work_id TEXT,
  source_chapter_label TEXT,
  source_unit_label TEXT,
  detail_json TEXT CHECK (detail_json IS NULL OR json_valid(detail_json)),
  created_at INTEGER NOT NULL,
  FOREIGN KEY (import_run_id) REFERENCES scripture_import_runs(id) ON DELETE RESTRICT,
  FOREIGN KEY (import_run_id, source_file_id)
    REFERENCES scripture_import_files(import_run_id, id) ON DELETE RESTRICT,
  FOREIGN KEY (work_id) REFERENCES scriptural_works(id) ON DELETE RESTRICT
);

CREATE TABLE scripture_import_run_events (
  id TEXT PRIMARY KEY NOT NULL,
  import_run_id TEXT NOT NULL,
  event_order INTEGER NOT NULL CHECK (event_order > 0),
  event_type TEXT NOT NULL,
  from_status TEXT,
  to_status TEXT,
  actor_ref TEXT,
  detail_json TEXT CHECK (detail_json IS NULL OR json_valid(detail_json)),
  created_at INTEGER NOT NULL,
  FOREIGN KEY (import_run_id) REFERENCES scripture_import_runs(id) ON DELETE RESTRICT,
  UNIQUE (import_run_id, event_order)
);

CREATE INDEX idx_scripture_import_runs_edition_status
  ON scripture_import_runs(edition_id, status, created_at);
CREATE INDEX idx_scripture_import_files_run_status
  ON scripture_import_files(import_run_id, parse_status);
CREATE INDEX idx_scripture_import_staging_lookup
  ON scripture_import_staging_units(import_run_id, work_id, source_chapter_order, source_unit_order);
CREATE INDEX idx_scripture_import_validation_run_severity
  ON scripture_import_validation_results(import_run_id, severity, result);

CREATE TRIGGER trg_scripture_import_runs_start_acquired
BEFORE INSERT ON scripture_import_runs
WHEN NEW.status <> 'acquired'
BEGIN
  SELECT RAISE(ABORT, 'an import run must start in acquired state');
END;

CREATE TRIGGER trg_scripture_import_run_status_transition
BEFORE UPDATE OF status ON scripture_import_runs
WHEN NEW.status <> OLD.status
AND NOT (
  (OLD.status = 'acquired' AND NEW.status IN ('inventoried', 'failed', 'rejected'))
  OR (OLD.status = 'inventoried' AND NEW.status IN ('parsed', 'failed', 'rejected'))
  OR (OLD.status = 'parsed' AND NEW.status IN ('validated', 'failed', 'rejected'))
  OR (OLD.status = 'validated' AND NEW.status IN ('reviewed', 'failed', 'rejected'))
  OR (OLD.status = 'reviewed' AND NEW.status IN ('published', 'failed', 'rejected'))
)
BEGIN
  SELECT RAISE(ABORT, 'invalid scripture import run status transition');
END;

CREATE TRIGGER trg_scripture_import_run_metadata_immutable
BEFORE UPDATE OF
  edition_id, versification_scheme_id, source_archive_url,
  source_archive_object_key, source_archive_sha256,
  source_archive_size_bytes, source_retrieved_at,
  parser_name, parser_version, parser_compatibility_profile,
  manifest_json
ON scripture_import_runs
WHEN
  NEW.edition_id <> OLD.edition_id
  OR NEW.versification_scheme_id <> OLD.versification_scheme_id
  OR NEW.source_archive_url <> OLD.source_archive_url
  OR NEW.source_archive_object_key <> OLD.source_archive_object_key
  OR NEW.source_archive_sha256 <> OLD.source_archive_sha256
  OR NEW.source_archive_size_bytes <> OLD.source_archive_size_bytes
  OR NEW.source_retrieved_at <> OLD.source_retrieved_at
  OR NEW.parser_name <> OLD.parser_name
  OR NEW.parser_version <> OLD.parser_version
  OR NEW.parser_compatibility_profile <> OLD.parser_compatibility_profile
  OR NEW.manifest_json <> OLD.manifest_json
BEGIN
  SELECT RAISE(ABORT, 'scripture import source provenance is immutable');
END;

CREATE TRIGGER trg_scripture_import_run_no_delete
BEFORE DELETE ON scripture_import_runs
BEGIN
  SELECT RAISE(ABORT, 'scripture import run records cannot be deleted');
END;

CREATE TRIGGER trg_scripture_import_files_parsed_payload
BEFORE INSERT ON scripture_import_files
WHEN NEW.parse_status = 'parsed'
AND (NEW.canonical_usx_object_key IS NULL OR NEW.canonical_usx_sha256 IS NULL)
BEGIN
  SELECT RAISE(ABORT, 'parsed source file requires canonical USX object key and checksum');
END;

CREATE TRIGGER trg_scripture_import_files_parsed_payload_update
BEFORE UPDATE OF parse_status, canonical_usx_object_key, canonical_usx_sha256
ON scripture_import_files
WHEN NEW.parse_status = 'parsed'
AND (NEW.canonical_usx_object_key IS NULL OR NEW.canonical_usx_sha256 IS NULL)
BEGIN
  SELECT RAISE(ABORT, 'parsed source file requires canonical USX object key and checksum');
END;

CREATE TRIGGER trg_scripture_import_files_no_change_after_publish
BEFORE UPDATE ON scripture_import_files
WHEN EXISTS (
  SELECT 1 FROM scripture_import_runs r
  WHERE r.id = OLD.import_run_id AND r.status = 'published'
)
BEGIN
  SELECT RAISE(ABORT, 'published import source-file inventory is immutable');
END;

CREATE TRIGGER trg_scripture_import_files_no_insert_after_publish
BEFORE INSERT ON scripture_import_files
WHEN EXISTS (
  SELECT 1 FROM scripture_import_runs r
  WHERE r.id = NEW.import_run_id AND r.status = 'published'
)
BEGIN
  SELECT RAISE(ABORT, 'published import source-file inventory is immutable');
END;

CREATE TRIGGER trg_scripture_import_units_no_change_after_publish
BEFORE UPDATE ON scripture_import_staging_units
WHEN EXISTS (
  SELECT 1 FROM scripture_import_runs r
  WHERE r.id = OLD.import_run_id AND r.status = 'published'
)
BEGIN
  SELECT RAISE(ABORT, 'published import staging units are immutable');
END;

CREATE TRIGGER trg_scripture_import_units_no_insert_after_publish
BEFORE INSERT ON scripture_import_staging_units
WHEN EXISTS (
  SELECT 1 FROM scripture_import_runs r
  WHERE r.id = NEW.import_run_id AND r.status = 'published'
)
BEGIN
  SELECT RAISE(ABORT, 'published import staging units are immutable');
END;

CREATE TRIGGER trg_scripture_import_units_no_delete_after_publish
BEFORE DELETE ON scripture_import_staging_units
WHEN EXISTS (
  SELECT 1 FROM scripture_import_runs r
  WHERE r.id = OLD.import_run_id AND r.status = 'published'
)
BEGIN
  SELECT RAISE(ABORT, 'published import staging units are immutable');
END;

CREATE TRIGGER trg_scripture_import_validation_no_update
BEFORE UPDATE ON scripture_import_validation_results
BEGIN
  SELECT RAISE(ABORT, 'import validation evidence is append-only');
END;

CREATE TRIGGER trg_scripture_import_validation_no_delete
BEFORE DELETE ON scripture_import_validation_results
BEGIN
  SELECT RAISE(ABORT, 'import validation evidence is append-only');
END;

CREATE TRIGGER trg_scripture_import_events_initial
AFTER INSERT ON scripture_import_runs
BEGIN
  INSERT INTO scripture_import_run_events (
    id, import_run_id, event_order, event_type, from_status,
    to_status, actor_ref, detail_json, created_at
  ) VALUES (
    'event-created-' || NEW.id, NEW.id, 1, 'run_created',
    NULL, NEW.status, NULL, NULL, NEW.created_at
  );
END;

CREATE TRIGGER trg_scripture_import_events_status
AFTER UPDATE OF status ON scripture_import_runs
WHEN NEW.status <> OLD.status
BEGIN
  INSERT INTO scripture_import_run_events (
    id, import_run_id, event_order, event_type, from_status,
    to_status, actor_ref, detail_json, created_at
  )
  SELECT
    lower(hex(randomblob(16))),
    NEW.id,
    COALESCE(MAX(event_order), 0) + 1,
    'status_changed',
    OLD.status,
    NEW.status,
    NEW.approved_by,
    json_object('failure_code', NEW.failure_code),
    NEW.updated_at
  FROM scripture_import_run_events
  WHERE import_run_id = NEW.id;
END;

CREATE TRIGGER trg_scripture_import_events_no_update
BEFORE UPDATE ON scripture_import_run_events
BEGIN
  SELECT RAISE(ABORT, 'import run events are append-only');
END;

CREATE TRIGGER trg_scripture_import_events_no_delete
BEFORE DELETE ON scripture_import_run_events
BEGIN
  SELECT RAISE(ABORT, 'import run events are append-only');
END;

CREATE TRIGGER trg_translation_edition_available_requires_import
BEFORE UPDATE OF status ON translation_editions
WHEN NEW.status = 'available'
AND OLD.status <> 'available'
AND NOT EXISTS (
  SELECT 1 FROM scripture_import_runs r
  WHERE r.edition_id = NEW.id AND r.status = 'published'
)
BEGIN
  SELECT RAISE(ABORT, 'translation edition requires a published import run');
END;
