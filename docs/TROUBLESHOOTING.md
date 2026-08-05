# Troubleshooting

## n8n does not start

- Symptom: container restarts or health check fails.
- Likely cause: database, memory, or encryption-key configuration.
- Diagnostic: `docker compose logs --tail=100 n8n` and `docker stats --no-stream`.
- Resolution: restore correct secret/database settings or controlled swap; keep rendering off the VM.
- Verification: `curl -fsS https://DOMAIN/healthz`.
- Rollback: restore the prior pinned image and configuration backup.

## Render validation fails

- Symptom: job reports invalid stream, duration, or dimensions.
- Likely cause: malformed input asset or FFmpeg filter/codec mismatch.
- Diagnostic: `ffprobe -v error -show_streams -show_format -of json OUTPUT.mp4`.
- Resolution: replace the asset or correct the deterministic render specification; do not bypass validation.
- Verification: run `pytest tests/test_renderer.py` and ffprobe again.
- Rollback: retain the previous validated content package; delete the failed temporary output.

## Publication is blocked

- Symptom: approved Reel does not publish.
- Likely cause: expired approval, unsupported claim, invalid render, token permission, or idempotency gate.
- Diagnostic: inspect the redacted workflow run by correlation ID and official container status.
- Resolution: correct evidence/render/token state and request a fresh approval; never reuse a callback.
- Verification: run the mock contract test, then one explicit sandbox publication.
- Rollback: set publication status to failed without removing the audit record; keep `AUTO_PUBLISH=false`.

