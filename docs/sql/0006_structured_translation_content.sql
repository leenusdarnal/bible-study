-- DRAFT ONLY. Requires migrations 0001–0005.
-- Preserve structured USFM-derived content instead of flattening all content into verse text.
-- translation_texts remains the searchable/display-text projection; this tree stores structure.

CREATE TABLE translation_content_blocks (
  id TEXT PRIMARY KEY NOT NULL,
  edition_id TEXT NOT NULL,
  versification_scheme_id TEXT NOT NULL,
  work_id TEXT NOT NULL,
  chapter_id TEXT,
  anchor_unit_id TEXT,
  block_order INTEGER NOT NULL CHECK (block_order > 0),
  block_type TEXT NOT NULL CHECK (block_type IN (
    'book_intro', 'chapter_heading', 'section_heading', 'paragraph',
    'poetry_line_group', 'list', 'colophon', 'peripheral', 'other'
  )),
  source_marker TEXT,
  source_member TEXT NOT NULL,
  source_order INTEGER NOT NULL CHECK (source_order > 0),
  metadata_json TEXT CHECK (metadata_json IS NULL OR json_valid(metadata_json)),
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  FOREIGN KEY (edition_id, versification_scheme_id)
    REFERENCES translation_editions(id, versification_scheme_id) ON DELETE RESTRICT,
  FOREIGN KEY (chapter_id, versification_scheme_id, work_id)
    REFERENCES scheme_chapters(id, scheme_id, work_id) ON DELETE RESTRICT,
  FOREIGN KEY (anchor_unit_id, versification_scheme_id, work_id)
    REFERENCES scripture_units(id, scheme_id, work_id) ON DELETE RESTRICT,
  UNIQUE (id, edition_id),
  UNIQUE (edition_id, source_member, source_order),
  CHECK (chapter_id IS NOT NULL OR anchor_unit_id IS NULL),
  CHECK (anchor_unit_id IS NULL OR chapter_id IS NOT NULL)
);

CREATE INDEX idx_translation_content_blocks_location
  ON translation_content_blocks(edition_id, work_id, chapter_id, block_order);
CREATE INDEX idx_translation_content_blocks_anchor
  ON translation_content_blocks(anchor_unit_id);

CREATE TABLE translation_content_nodes (
  id TEXT PRIMARY KEY NOT NULL,
  block_id TEXT NOT NULL,
  parent_node_id TEXT,
  node_order_path TEXT NOT NULL,
  node_type TEXT NOT NULL CHECK (node_type IN (
    'text', 'span', 'footnote', 'cross_reference', 'milestone',
    'unknown_marker', 'attribute', 'break'
  )),
  source_marker TEXT,
  text_content TEXT,
  attributes_json TEXT CHECK (attributes_json IS NULL OR json_valid(attributes_json)),
  raw_value TEXT,
  source_order INTEGER NOT NULL CHECK (source_order > 0),
  created_at INTEGER NOT NULL,
  FOREIGN KEY (block_id) REFERENCES translation_content_blocks(id) ON DELETE RESTRICT,
  FOREIGN KEY (parent_node_id, block_id)
    REFERENCES translation_content_nodes(id, block_id) ON DELETE RESTRICT,
  UNIQUE (id, block_id),
  UNIQUE (block_id, node_order_path),
  CHECK (parent_node_id IS NULL OR parent_node_id <> id)
);

CREATE INDEX idx_translation_content_nodes_parent_order
  ON translation_content_nodes(block_id, parent_node_id, source_order);

CREATE UNIQUE INDEX idx_translation_content_blocks_chapter_order
  ON translation_content_blocks(edition_id, work_id, chapter_id, block_order)
  WHERE chapter_id IS NOT NULL;
CREATE UNIQUE INDEX idx_translation_content_blocks_book_order
  ON translation_content_blocks(edition_id, work_id, block_order)
  WHERE chapter_id IS NULL;
CREATE UNIQUE INDEX idx_translation_content_nodes_source_order
  ON translation_content_nodes(block_id, source_order);

CREATE TRIGGER trg_translation_content_block_anchor_insert
BEFORE INSERT ON translation_content_blocks
WHEN NEW.anchor_unit_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM scripture_units u
  WHERE u.id = NEW.anchor_unit_id
    AND u.scheme_id = NEW.versification_scheme_id
    AND u.work_id = NEW.work_id
    AND u.chapter_id = NEW.chapter_id
)
BEGIN
  SELECT RAISE(ABORT, 'content block anchor must belong to its declared chapter');
END;

CREATE TRIGGER trg_translation_content_block_anchor_update
BEFORE UPDATE OF anchor_unit_id, chapter_id, work_id, versification_scheme_id
ON translation_content_blocks
WHEN NEW.anchor_unit_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM scripture_units u
  WHERE u.id = NEW.anchor_unit_id
    AND u.scheme_id = NEW.versification_scheme_id
    AND u.work_id = NEW.work_id
    AND u.chapter_id = NEW.chapter_id
)
BEGIN
  SELECT RAISE(ABORT, 'content block anchor must belong to its declared chapter');
END;
