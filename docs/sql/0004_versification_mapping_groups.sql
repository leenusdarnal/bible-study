-- DRAFT ONLY. Requires 0001_scripture_core.sql.
-- Add explicit grouping for non-one-to-one versification relationships.
-- Existing pairwise mapping rows are preserved and remain ungrouped until reviewed.

CREATE TABLE scripture_mapping_groups (
  id TEXT PRIMARY KEY NOT NULL,
  from_scheme_id TEXT NOT NULL,
  to_scheme_id TEXT NOT NULL,
  group_type TEXT NOT NULL
    CHECK (group_type IN (
      'equivalent', 'split', 'combined', 'moved', 'subverse',
      'partial', 'approximate', 'absent', 'complex'
    )),
  source_id TEXT,
  source_reference TEXT,
  confidence TEXT NOT NULL DEFAULT 'unreviewed'
    CHECK (confidence IN ('unreviewed', 'high', 'medium', 'low', 'disputed')),
  review_status TEXT NOT NULL DEFAULT 'pending'
    CHECK (review_status IN ('pending', 'approved', 'rejected')),
  rationale TEXT,
  notes TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  FOREIGN KEY (from_scheme_id) REFERENCES versification_schemes(id) ON DELETE RESTRICT,
  FOREIGN KEY (to_scheme_id) REFERENCES versification_schemes(id) ON DELETE RESTRICT,
  UNIQUE (id, from_scheme_id, to_scheme_id),
  CHECK (from_scheme_id <> to_scheme_id)
);

CREATE TABLE scripture_mapping_group_members (
  id TEXT PRIMARY KEY NOT NULL,
  mapping_group_id TEXT NOT NULL,
  from_scheme_id TEXT NOT NULL,
  to_scheme_id TEXT NOT NULL,
  side TEXT NOT NULL CHECK (side IN ('from', 'to')),
  scheme_id TEXT NOT NULL,
  unit_id TEXT NOT NULL,
  member_order INTEGER NOT NULL CHECK (member_order > 0),
  FOREIGN KEY (mapping_group_id, from_scheme_id, to_scheme_id)
    REFERENCES scripture_mapping_groups(id, from_scheme_id, to_scheme_id) ON DELETE CASCADE,
  FOREIGN KEY (unit_id, scheme_id)
    REFERENCES scripture_units(id, scheme_id) ON DELETE RESTRICT,
  UNIQUE (mapping_group_id, side, unit_id),
  UNIQUE (mapping_group_id, side, member_order),
  CHECK (
    (side = 'from' AND scheme_id = from_scheme_id)
    OR (side = 'to' AND scheme_id = to_scheme_id)
  )
);

ALTER TABLE scripture_unit_mappings RENAME TO scripture_unit_mappings_legacy;

CREATE TABLE scripture_unit_mappings (
  id TEXT PRIMARY KEY NOT NULL,
  from_unit_id TEXT NOT NULL,
  from_scheme_id TEXT NOT NULL,
  to_unit_id TEXT NOT NULL,
  to_scheme_id TEXT NOT NULL,
  mapping_group_id TEXT,
  mapping_type TEXT NOT NULL
    CHECK (mapping_type IN ('equivalent', 'split', 'combined', 'partial', 'approximate')),
  source_id TEXT,
  confidence TEXT NOT NULL DEFAULT 'unreviewed'
    CHECK (confidence IN ('unreviewed', 'high', 'medium', 'low', 'disputed')),
  notes TEXT,
  review_status TEXT NOT NULL DEFAULT 'pending'
    CHECK (review_status IN ('pending', 'approved', 'rejected')),
  created_at INTEGER NOT NULL,
  FOREIGN KEY (from_unit_id, from_scheme_id)
    REFERENCES scripture_units(id, scheme_id) ON DELETE RESTRICT,
  FOREIGN KEY (to_unit_id, to_scheme_id)
    REFERENCES scripture_units(id, scheme_id) ON DELETE RESTRICT,
  FOREIGN KEY (mapping_group_id, from_scheme_id, to_scheme_id)
    REFERENCES scripture_mapping_groups(id, from_scheme_id, to_scheme_id) ON DELETE RESTRICT,
  CHECK (from_unit_id <> to_unit_id),
  CHECK (from_scheme_id <> to_scheme_id)
);

INSERT INTO scripture_unit_mappings (
  id, from_unit_id, from_scheme_id, to_unit_id, to_scheme_id,
  mapping_group_id, mapping_type, source_id, confidence, notes, review_status, created_at
)
SELECT
  id, from_unit_id, from_scheme_id, to_unit_id, to_scheme_id,
  NULL, mapping_type, source_id, confidence, notes, review_status, created_at
FROM scripture_unit_mappings_legacy;

DROP TABLE scripture_unit_mappings_legacy;

CREATE INDEX idx_scripture_mapping_groups_from_scheme
  ON scripture_mapping_groups(from_scheme_id, review_status);
CREATE INDEX idx_scripture_mapping_groups_to_scheme
  ON scripture_mapping_groups(to_scheme_id, review_status);
CREATE INDEX idx_scripture_mapping_members_group_side
  ON scripture_mapping_group_members(mapping_group_id, side, member_order);
CREATE INDEX idx_scripture_unit_mappings_group
  ON scripture_unit_mappings(mapping_group_id);

CREATE TRIGGER trg_mapping_edge_membership_insert
BEFORE INSERT ON scripture_unit_mappings
WHEN NEW.mapping_group_id IS NOT NULL
AND (
  NOT EXISTS (
    SELECT 1 FROM scripture_mapping_group_members m
    WHERE m.mapping_group_id = NEW.mapping_group_id
      AND m.side = 'from'
      AND m.scheme_id = NEW.from_scheme_id
      AND m.unit_id = NEW.from_unit_id
  )
  OR NOT EXISTS (
    SELECT 1 FROM scripture_mapping_group_members m
    WHERE m.mapping_group_id = NEW.mapping_group_id
      AND m.side = 'to'
      AND m.scheme_id = NEW.to_scheme_id
      AND m.unit_id = NEW.to_unit_id
  )
)
BEGIN
  SELECT RAISE(ABORT, 'mapping edge units must belong to the selected mapping group');
END;

CREATE TRIGGER trg_mapping_edge_membership_update
BEFORE UPDATE OF mapping_group_id, from_unit_id, from_scheme_id, to_unit_id, to_scheme_id
ON scripture_unit_mappings
WHEN NEW.mapping_group_id IS NOT NULL
AND (
  NOT EXISTS (
    SELECT 1 FROM scripture_mapping_group_members m
    WHERE m.mapping_group_id = NEW.mapping_group_id
      AND m.side = 'from'
      AND m.scheme_id = NEW.from_scheme_id
      AND m.unit_id = NEW.from_unit_id
  )
  OR NOT EXISTS (
    SELECT 1 FROM scripture_mapping_group_members m
    WHERE m.mapping_group_id = NEW.mapping_group_id
      AND m.side = 'to'
      AND m.scheme_id = NEW.to_scheme_id
      AND m.unit_id = NEW.to_unit_id
  )
)
BEGIN
  SELECT RAISE(ABORT, 'mapping edge units must belong to the selected mapping group');
END;
