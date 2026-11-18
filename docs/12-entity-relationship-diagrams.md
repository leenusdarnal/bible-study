# 12. Entity Relationship Diagrams

- **Status:** Proposed logical ERDs aligned with [Database Schema Proposal](11-database-schema.md).
- **Notation:** Mermaid ER diagrams.
- **Important:** These diagrams are not generated from deployed migrations. Update them whenever the physical schema changes.

## 12.1 Scripture, canon and translations

~~~mermaid
erDiagram
    SCRIPTURAL_WORKS ||--o{ CANON_BOOKS : appears_as
    CANONS ||--|{ CANON_BOOKS : contains
    SCRIPTURAL_WORKS ||--o{ SCHEME_CHAPTERS : divided_into
    VERSIFICATION_SCHEMES ||--|{ SCHEME_CHAPTERS : defines
    SCHEME_CHAPTERS ||--|{ SCRIPTURE_UNITS : contains
    VERSIFICATION_SCHEMES ||--|{ SCRIPTURE_UNITS : numbers
    VERSIFICATION_SCHEMES ||--o{ TRANSLATION_EDITIONS : used_by
    TRANSLATION_EDITIONS ||--o{ TRANSLATION_TEXTS : contains
    SCRIPTURE_UNITS ||--o{ TRANSLATION_TEXTS : receives_text
    SCRIPTURE_UNITS ||--o{ SCRIPTURE_UNIT_MAPPINGS : source_unit
    SCRIPTURE_UNITS ||--o{ SCRIPTURE_UNIT_MAPPINGS : target_unit
    PASSAGE_REFERENCES ||--|{ PASSAGE_REFERENCE_SEGMENTS : has
    SCRIPTURE_UNITS ||--o{ PASSAGE_REFERENCE_SEGMENTS : start_unit
    SCRIPTURE_UNITS ||--o{ PASSAGE_REFERENCE_SEGMENTS : end_unit
~~~

**Interpretation:** work identity, canon order and verse numbering are separate. Translation text uses its edition's scheme. Mapping groups preserve complete ordered source and target unit sets for one-to-many, many-to-one and many-to-many relationships; pairwise mapping edges are optional links within those groups.

## 12.2 Entities and knowledge graph

~~~mermaid
erDiagram
    ENTITIES ||--o| PEOPLE : details
    ENTITIES ||--o| PLACES : details
    ENTITIES ||--o| EVENTS : details
    ENTITIES ||--o| GROUPS : details
    ENTITIES ||--o| OBJECTS : details
    ENTITIES ||--o| THEMES : details
    ENTITIES ||--o{ ENTITY_NAMES : has
    ENTITIES ||--o{ ENTITY_EXTERNAL_IDS : identified_in
    ENTITIES ||--o{ ENTITY_PASSAGES : associated_with
    PASSAGE_REFERENCES ||--o{ ENTITY_PASSAGES : references
    ENTITIES ||--o{ ENTITY_RELATIONSHIPS : subject
    ENTITIES ||--o{ ENTITY_RELATIONSHIPS : object
    RELATIONSHIP_TYPES ||--o{ ENTITY_RELATIONSHIPS : classifies
    ENTITY_RELATIONSHIPS ||--o{ RELATIONSHIP_EVIDENCE : supported_by
~~~

Specialised entity tables are optional one-to-one extensions. Each graph edge has a type and evidence explaining why it exists.

## 12.3 Sources, claims and research evidence

~~~mermaid
erDiagram
    SOURCES ||--o{ SOURCE_VERSIONS : has
    SOURCES ||--o{ CITATIONS : cited_by
    SOURCE_VERSIONS ||--o{ CITATIONS : locates
    LICENCES ||--o{ SOURCES : governs
    CLAIMS ||--o{ CLAIM_EVIDENCE : assessed_by
    CITATIONS ||--o{ CLAIM_EVIDENCE : evidences
    PASSAGE_REFERENCES ||--o{ CLAIM_EVIDENCE : relates_to
    RESEARCH_ARTICLES ||--o{ RESEARCH_ARTICLE_CLAIMS : discusses
    CLAIMS ||--o{ RESEARCH_ARTICLE_CLAIMS : included_in
    PASSAGE_REFERENCES ||--o{ TEXTUAL_VARIANTS : location
    TEXTUAL_VARIANTS ||--|{ VARIANT_READINGS : contains
    MANUSCRIPTS ||--o{ VARIANT_READINGS : attests
    SOURCES ||--o{ MANUSCRIPTS : catalogues
~~~

A source, its version and an exact citation locator are distinct records. Claims connect evidence to propositions; supporting, challenging and contextual evidence can coexist.

## 12.4 Study content, editorial review and personal library

~~~mermaid
erDiagram
    CONTENT_ITEMS ||--|{ CONTENT_REVISIONS : versioned_as
    CONTENT_ITEMS ||--o{ CONTENT_PASSAGES : covers
    CONTENT_ITEMS ||--o{ CONTENT_ENTITIES : discusses
    CONTENT_ITEMS ||--o{ CONTENT_CITATIONS : cites
    PASSAGE_REFERENCES ||--o{ CONTENT_PASSAGES : referenced_by
    ENTITIES ||--o{ CONTENT_ENTITIES : referenced_by
    CITATIONS ||--o{ CONTENT_CITATIONS : attached_to
    CONTRIBUTIONS ||--o{ REVIEWS : reviewed_by
    USERS ||--o{ CONTRIBUTIONS : submits
    USERS ||--o{ REVIEWS : performs
    USERS ||--o{ USER_NOTES : owns
    USER_NOTES ||--o{ NOTE_PASSAGES : links
    PASSAGE_REFERENCES ||--o{ NOTE_PASSAGES : referenced_by
    USERS ||--o{ USER_BOOKMARKS : owns
    USERS ||--o{ USER_HIGHLIGHTS : owns
    USERS ||--o{ READING_TRACKERS : owns
    READING_TRACKERS ||--o{ READING_TRACKER_BOOKS : selects
    READING_TRACKERS ||--o{ READING_TRACKER_CHAPTER_PROGRESS : records
    SCHEME_CHAPTERS ||--o{ READING_TRACKER_CHAPTER_PROGRESS : chapter_state
    CANONS ||--o{ READING_TRACKERS : defines_scope
    VERSIFICATION_SCHEMES ||--o{ READING_TRACKERS : numbers_chapters
    CANON_BOOKS ||--o{ READING_TRACKER_BOOKS : selected_from
    CANON_BOOKS ||--o{ READING_TRACKER_CHAPTER_PROGRESS : validates_work
    PASSAGE_REFERENCES ||--o{ USER_BOOKMARKS : bookmarked
    PASSAGE_REFERENCES ||--o{ USER_HIGHLIGHTS : highlighted
~~~

The USERS node represents the eventual authentication provider's user record; use its actual table name and key after the auth proof of concept. Private library records must be owner-scoped. Guest trackers are stored locally in IndexedDB and do not appear as cloud user rows. Reading plans and chapter tracker progress remain separate.

## 12.5 Import and provenance lifecycle

~~~mermaid
flowchart TD
    A[External dataset and licence] --> B[Immutable source snapshot in R2]
    B --> C[Dataset version record in D1]
    C --> D[Import run]
    D --> E[Staged raw records]
    E --> F{Validation and reconciliation}
    F -->|Invalid| G[Rejected record with reason]
    F -->|New or matched| H[Review queue]
    H --> I{Editorial decision}
    I -->|Reject| G
    I -->|Approve| J[Published domain records]
    J --> K[Search projection and application]
    J --> L[Audit and provenance links]
~~~

An import must be repeatable without duplicating published entities. Original source snapshots and external identifiers remain available for reconciliation and rollback.

## 12.6 Cross-domain invariants

- Every passage segment endpoint references a Scripture unit.
- Translation text units belong to the edition's declared scheme.
- Every published research claim has traceable evidence and editorial status.
- Every knowledge-graph edge has a type and recorded evidence or a documented exception.
- Every imported entity retains its external ID and dataset version.
- Every private library record belongs to one user unless sharing is explicitly introduced.
- Tracker chapter progress belongs to the tracker's canon and versification scheme.
- Selected-book trackers accept new progress only for selected books; excluded historical progress may remain stored but is omitted from current statistics.
- Published content points to an approved revision.
- Source retirement does not delete dependent citations.
- Entity merges preserve links and can be reversed.

## 12.7 Validation checklist

Before accepting the ERD:
- Generate diagrams from actual Drizzle schema/migrations where practical.
- Run migrations on a clean D1 database and an upgrade database.
- Test foreign-key enforcement, unique constraints and retirement/deletion behaviour.
- Load verse divisions with one-to-one and many-to-many mappings.
- Test multi-segment passage references.
- Switch translations while preserving a note and highlight.
- Test entity merge/rollback with relationships and citations.
- Test user ownership isolation and reviewer separation.
- Test multiple trackers, selected-book scope and chapter-level completion.
- Compare every diagram to implemented tables and foreign keys.
~~~
