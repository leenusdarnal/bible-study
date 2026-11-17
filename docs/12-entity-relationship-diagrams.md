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
    SCRIPTURAL_WORKS { text id PK text osis_code text standard_name }
    CANONS { text id PK text code UK text name }
    CANON_BOOKS { text id PK text canon_id FK text work_id FK integer position }
    VERSIFICATION_SCHEMES { text id PK text code UK text name }
    SCHEME_CHAPTERS { text id PK text scheme_id FK text work_id FK text chapter_label }
    SCRIPTURE_UNITS { text id PK text scheme_id FK text work_id FK text chapter_id FK text unit_label }
    SCRIPTURE_UNIT_MAPPINGS { text id PK text from_unit_id FK text to_unit_id FK text mapping_type }
    TRANSLATION_EDITIONS { text id PK text versification_scheme_id FK text licence_id FK }
    TRANSLATION_TEXTS { text id PK text edition_id FK text scripture_unit_id FK text text }
    PASSAGE_REFERENCES { text id PK text reference_scheme_id FK text label }
    PASSAGE_REFERENCE_SEGMENTS { text id PK text passage_reference_id FK text start_unit_id FK text end_unit_id FK integer segment_order }
~~~

**Interpretation:** work identity, canon order and verse numbering are separate. Translation text uses its edition's scheme; explicit mapping handles non-one-to-one alignment.

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
    ENTITIES { text id PK text entity_type text preferred_name text status }
    PEOPLE { text entity_id PK,FK }
    PLACES { text entity_id PK,FK }
    EVENTS { text entity_id PK,FK }
    GROUPS { text entity_id PK,FK }
    OBJECTS { text entity_id PK,FK }
    THEMES { text entity_id PK,FK }
    ENTITY_NAMES { text id PK text entity_id FK text name text name_type }
    ENTITY_EXTERNAL_IDS { text id PK text entity_id FK text dataset_id FK text external_id }
    ENTITY_PASSAGES { text id PK text entity_id FK text passage_reference_id FK }
    RELATIONSHIP_TYPES { text id PK text code UK text label }
    ENTITY_RELATIONSHIPS { text id PK text subject_entity_id FK text relationship_type_id FK text object_entity_id FK }
    RELATIONSHIP_EVIDENCE { text id PK text relationship_id FK text passage_reference_id FK text citation_id FK }
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
    SOURCES { text id PK text title text source_type text licence_id FK }
    SOURCE_VERSIONS { text id PK text source_id FK text checksum text r2_object_key }
    LICENCES { text id PK text code UK text licence_url }
    CITATIONS { text id PK text source_id FK text source_version_id FK text locator }
    CLAIMS { text id PK text claim_text text claim_type text status }
    CLAIM_EVIDENCE { text id PK text claim_id FK text citation_id FK text passage_reference_id FK text evidence_relation }
    RESEARCH_ARTICLES { text id PK text title text current_revision_id }
    RESEARCH_ARTICLE_CLAIMS { text id PK text article_id FK text claim_id FK }
    MANUSCRIPTS { text id PK text name text siglum }
    TEXTUAL_VARIANTS { text id PK text passage_reference_id FK text description }
    VARIANT_READINGS { text id PK text variant_id FK text manuscript_id FK text reading_text }
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
    USERS ||--o{ USER_READING_PROGRESS : tracks
    PASSAGE_REFERENCES ||--o{ USER_BOOKMARKS : bookmarked
    PASSAGE_REFERENCES ||--o{ USER_HIGHLIGHTS : highlighted
    PASSAGE_REFERENCES ||--o{ USER_READING_PROGRESS : tracked
    CONTENT_ITEMS { text id PK text content_type text title text current_revision_id text editorial_status }
    CONTENT_REVISIONS { text id PK text content_item_id FK integer revision_number text body_markdown }
    CONTENT_PASSAGES { text id PK text content_item_id FK text passage_reference_id FK }
    CONTENT_ENTITIES { text id PK text content_item_id FK text entity_id FK }
    CONTENT_CITATIONS { text id PK text content_item_id FK text citation_id FK }
    USERS { text id PK }
    USER_NOTES { text id PK text user_id FK text body_markdown }
    NOTE_PASSAGES { text id PK text note_id FK text passage_reference_id FK }
    USER_BOOKMARKS { text id PK text user_id FK text passage_reference_id FK }
    USER_HIGHLIGHTS { text id PK text user_id FK text passage_reference_id FK }
    USER_READING_PROGRESS { text id PK text user_id FK text passage_reference_id FK }
    CONTRIBUTIONS { text id PK text contributor_user_id FK text status }
    REVIEWS { text id PK text contribution_id FK text reviewer_user_id FK text decision }
~~~

The USERS node represents the eventual authentication provider's user record; use its actual table name and key after the auth proof of concept. Private library records must be owner-scoped.

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
- Compare every diagram to implemented tables and foreign keys.
~~~
