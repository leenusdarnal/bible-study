-- DRAFT ONLY. Requires 0001_scripture_core.sql.
-- Distinguish text-bearing verses from source markers that carry only notes
-- or that are explicitly empty. This prevents note-only USFM anchors from
-- being mistaken for missing/failed Bible text during import.

ALTER TABLE translation_texts
ADD COLUMN content_state TEXT NOT NULL DEFAULT 'text'
  CHECK (content_state IN ('text', 'annotation_only', 'empty_marker'));

CREATE TRIGGER trg_translation_text_content_state_insert
BEFORE INSERT ON translation_texts
WHEN
  (NEW.content_state = 'text' AND length(trim(NEW.text)) = 0)
  OR (
    NEW.content_state = 'annotation_only'
    AND (length(trim(NEW.text)) <> 0 OR NEW.footnote_metadata_json IS NULL)
  )
  OR (
    NEW.content_state = 'empty_marker'
    AND (length(trim(NEW.text)) <> 0 OR NEW.footnote_metadata_json IS NOT NULL)
  )
BEGIN
  SELECT RAISE(ABORT, 'translation text does not match its content state');
END;

CREATE TRIGGER trg_translation_text_content_state_update
BEFORE UPDATE OF content_state, text, footnote_metadata_json
ON translation_texts
WHEN
  (NEW.content_state = 'text' AND length(trim(NEW.text)) = 0)
  OR (
    NEW.content_state = 'annotation_only'
    AND (length(trim(NEW.text)) <> 0 OR NEW.footnote_metadata_json IS NULL)
  )
  OR (
    NEW.content_state = 'empty_marker'
    AND (length(trim(NEW.text)) <> 0 OR NEW.footnote_metadata_json IS NOT NULL)
  )
BEGIN
  SELECT RAISE(ABORT, 'translation text does not match its content state');
END;
