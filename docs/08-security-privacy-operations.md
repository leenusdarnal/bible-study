# 8. Security, Privacy and Operations

## 8.1 Guest access

All public Bible and research content should be accessible without registration. Accounts are required only for personal features and synchronisation.

## 8.2 Roles

Initial role model:
- **User:** private notes, bookmarks, highlights, progress and preferences.
- **Contributor:** submit corrections, sources and proposed content.
- **Reviewer:** review assigned subjects and recommend decisions.
- **Editor:** edit and publish content after required review.
- **Administrator:** manage platform settings, roles, governance and oversight.

Permissions must be enforced server-side. Support multiple roles only with explicit permission boundaries. Contributors must not approve their own submissions.

## 8.3 Editorial oversight

Specialist reviewers assess subject-specific accuracy. Editors approve publication after checking evidence, clarity and licensing. Administrators oversee governance and auditability.

## 8.4 Authentication

Required direction:
- Email/password.
- Optional social login.
- Optional two-factor authentication, with stronger requirements for privileged roles.
- Secure session management.
- Password reset and recovery.
- Login rate limiting and abuse protection.
- Cloudflare Turnstile for appropriate public forms and account flows.

Better Auth is the candidate, pending a compatibility and security proof of concept with SvelteKit, Workers, D1 and Drizzle.

## 8.5 Privacy controls

Users should be able to:
- Export their personal data.
- Request account and personal-data deletion.
- View and revoke active sessions.
- Manage consent and optional data processing.
- Control personalisation.
- Understand what data is collected and why.

Collect only necessary data. Keep private user records separate from public research. Explain lawful retention and deletion limitations transparently.

## 8.6 Audit and access control

Record important privileged actions: role changes, publication decisions, content edits, imports, merges, corrections and security-sensitive account events. Restrict access to audit logs and protect them from unauthorised modification.

## 8.7 Backups and disaster recovery

Requirements:
- Automated D1 backups using supported capabilities.
- Scheduled independent exports of critical structured data.
- Off-site or separately controlled copies of important data and R2 objects.
- Versioned import snapshots and editorial records.
- Restricted and encrypted backup access.
- Documented recovery objectives and procedures.
- Regular restoration tests in a separate environment.

A backup is not considered proven until restoration has been tested. An additional bucket alone may not provide sufficient account-level disaster isolation. Verify current Cloudflare R2 versioning, replication and backup capabilities before implementation.

## 8.8 Operational environments

Use separate development, preview and production resources. Protect secrets, apply least privilege, log operational failures and define a rollback procedure for deployments and migrations.
