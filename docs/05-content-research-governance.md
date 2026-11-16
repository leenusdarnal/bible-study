# 5. Content and Research Governance

## 5.1 Data import policy

All third-party datasets follow a controlled pipeline:

1. **Staging:** preserve original files and source metadata.
2. **Validation:** check schema, required fields, licence, references, identifiers and data quality.
3. **Reconciliation:** detect duplicates and map source identifiers to platform identities.
4. **Review:** route uncertain, disputed or high-impact records to qualified reviewers.
5. **Publication:** publish only approved records.
6. **Monitoring:** check upstream versions and import updates through controlled releases.

Never import directly into production without validation and an auditable process.

## 5.2 Duplicate entity detection

Use automated candidate matching with human approval for uncertain matches.

Signals may include:
- Names and aliases.
- Source identifiers.
- Scripture references.
- Entity type.
- Relationships and context.
- Historical/geographical attributes.

Do not automatically merge records merely because their names are similar. Preserve aliases, original source IDs and merge history. Provide a way to reverse an incorrect merge.

## 5.3 Content creation

Use a combination of:
- Original human editorial writing.
- AI-assisted drafts in a future phase.
- Properly licensed scholarly and historical sources.

Substantive claims need citations and editorial review appropriate to their importance. AI-generated content remains a draft until approved. Never invent citations or imply that paraphrased or adapted source material is original.

## 5.4 Dataset updates

Automated version checks followed by controlled imports. Maintain a dataset registry with:
- Provider and dataset name.
- Source URL and licence.
- Current imported version and latest detected version.
- Last checked/imported timestamps.
- Checksums and change summary.
- Import status, validation results and approval.
- Transformation version and logs.

Updates must preserve previous approved versions and avoid silently overwriting editorial corrections.

## 5.5 Sources and research records

Research-grade source metadata should include:
- Author or institution.
- Title and publication.
- Publisher and publication date.
- URL or stable identifier.
- Page, section or location in the source.
- Quotation/paraphrase relationship.
- Copyright and licence.
- Source version and retrieval date.
- Editorial verification status.
- Claims, passages and entities supported or discussed.

Evidence may support, contextualise, challenge or be unrelated to a claim. Do not overstate what a source proves.

## 5.6 Evidence and publication states

Suggested labels:
- Unreviewed.
- Validated.
- Source-verified.
- Editorially reviewed.
- Disputed.
- Corrected/superseded.
- Rejected.

Keep provenance and review status separate from theological truth claims. Confidence labels describe evidence quality, not the probability of a religious belief.

## 5.7 Community contributions

Allow suggestions for corrections, missing references, source additions, geographical identifications, alternative interpretations and translation/versification issues.

Workflow:
1. Submission.
2. Automated checks.
3. Triage and assignment.
4. Specialist review where needed.
5. Editorial decision.
6. Publication or rejection with reason.
7. Permanent revision history.

Community submissions are not verified facts until reviewed and approved.

## 5.8 Specialist review and editorial roles

Specialist reviewers assess subject-specific accuracy. Editors review sourcing, clarity, licensing and publication readiness. Administrators oversee governance, permissions and auditability.

No contributor should approve their own submission. Avoid conflicts of interest and retain reviewer identity and decision history.
