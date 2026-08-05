# Test report

Date: 2026-08-05

- Pytest: 18 passed.
- Core coverage: 84.83% (threshold 80%).
- Ruff: passed after final formatting fix.
- Mypy strict: passed for application source.
- Alembic: initial migration upgrade, downgrade, and second upgrade passed.
- Workflow validator: ten secret-free JSON exports passed structural checks.
- Compose: configuration parsed, images built, PostgreSQL healthy, n8n returned HTTP 200 at `/healthz`.
- Browser: n8n owner setup completed; all ten imported workflows appeared in the UI and WF-01 opened with both exported nodes visible.

Pending: full synthetic H.264/AAC render, Piper narration, detailed credentialed n8n nodes, GitHub-hosted Actions run, and all credentialed contract/sandbox checks.
