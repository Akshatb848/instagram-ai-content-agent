# Implementation Status

Last updated: 2026-08-05

## Baseline audit

- Workspace was empty and was not a Git repository.
- No application code, credentials, infrastructure, or workflows existed.
- Two supplied briefs conflicted on the default host. Decision ADR-001 selects the later zero-cost architecture: n8n on one eligible Google Compute Engine e2-micro VM and rendering on GitHub Actions. Cloud Run remains an optional deployment profile.
- Live publication is disabled by default and is never exercised by automated tests.

## Phase status

| Phase | Status | Acceptance criteria | Missing external inputs |
| --- | --- | --- | --- |
| 0. Repository and architecture | COMPLETE | Baseline, ADR, checklist, credential inventory, repository skills | None |
| 1. Foundation and database | COMPLETE | Installable app, configuration validation, models, migration, seed data | None (SQLite local) |
| 2. Source ingestion | COMPLETE | Safe normalization, URL canonicalization, duplicate rejection | Live feed contract verification pending |
| 3. Ranking and verification | COMPLETE | Deterministic score explanations; unsupported claims blocked | None |
| 4. Content generation | COMPLETE | Gemini/Ollama/mock abstraction and validated structured package | Gemini key only for live calls |
| 5. Renderer | IN_PROGRESS | Synthetic 1080x1920 MP4, subtitles, cover, manifest, ffprobe pass | Piper voice/model and full synthetic render pending |
| 6. GitHub Actions | IN_PROGRESS | Test, security, and bounded render workflows | GitHub repository/secrets for live dispatch |
| 7. n8n workflows | BLOCKED_EXTERNAL_APPROVAL | Ten importable, secret-free workflow exports | User must create local n8n owner before UI import verification |
| 8. Telegram approval | NOT_STARTED | Signed, expiring, replay-safe authorised callbacks | Telegram bot token/user ID for sandbox verification |
| 9. Instagram publication | NOT_STARTED | Idempotent official API adapter; mocks pass; live off | Meta app, professional account, permissions/token |
| 10. Cloud deployment | NOT_STARTED | Idempotent e2-micro Docker deployment and rollback docs | GCP project/billing confirmation/domain |
| 11. QA and handover | NOT_STARTED | Quality gates, reports, runbooks, manual-actions list | External integration credentials for live verification |

## Phase log

### Phase 0

- Acceptance criteria: record empty baseline; resolve architecture; enumerate credentials; create implementation plan and repository-scoped skills; initialize Git.
- Files created/modified: this file, `docs/ARCHITECTURE.md`, `docs/adr/001-zero-cost-deployment.md`, `.agents/skills/*`.
- Blockers: none for local implementation.

### Verification snapshot

- 18 tests passed; core coverage 84.83%.
- Ruff and strict mypy passed after the latest source changes.
- Alembic upgrade/downgrade/upgrade passed.
- Ten workflow JSON files passed structural and embedded-secret validation.
- Docker Compose built; PostgreSQL became healthy; n8n health endpoint returned HTTP 200.
- In-app browser reached the n8n owner setup screen.
- Dependency audit is pending because this Windows Python environment rejects the local TLS certificate chain when contacting PyPI; CI runs the same audit on Ubuntu.
- n8n UI import is blocked until the owner account is created by the user.
