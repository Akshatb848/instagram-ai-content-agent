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
| 7. n8n workflows | IN_PROGRESS | Ten importable, secret-free workflow exports | Credentialed operational nodes and activation pending |
| 8. Telegram approval | NOT_STARTED | Signed, expiring, replay-safe authorised callbacks | Telegram bot token/user ID for sandbox verification |
| 9. Instagram publication | NOT_STARTED | Idempotent official API adapter; mocks pass; live off | Meta app, professional account, permissions/token |
| 10. Zero-cost deployment | IN_PROGRESS | Owner-operated Docker host plus Tailscale Funnel, restart and rollback verification | Tailscale approval and public endpoint verification |
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
- User created the local owner. n8n was upgraded to 1.121.0 after its critical-update warning.
- CLI import reported ten successful imports; the UI showed all ten, total 10, inactive.
- WF-01 opened in the editor with its Manual Trigger and Status nodes visible.
- Dependency audit is pending because this Windows Python environment rejects the local TLS certificate chain when contacting PyPI; CI runs the same audit on Ubuntu.
- Production activation remains blocked until signed webhook and provider credentials are configured.
- Google Cloud was removed after the owner confirmed its free tier was exhausted. The active profile is an already-owned always-on host plus Tailscale Funnel; systematic external setup is documented in `docs/EXTERNAL_SETUP.md`.
