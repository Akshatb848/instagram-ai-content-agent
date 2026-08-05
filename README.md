# Instagram AI Content Agent

A zero-cost-first, human-approved pipeline that discovers trustworthy AI updates, rejects duplicates and unsupported claims, creates a structured Reel package, renders deterministic vertical video, and publishes only through the official Instagram API after Telegram approval.

## Safe local start

1. Install Python 3.11, Docker Desktop, Node.js, and FFmpeg.
2. Copy `.env.example` to `.env`; keep `LLM_PROVIDER=mock`, `AUTO_PUBLISH=false`, and `ALLOW_PAID_FALLBACK=false`.
3. Run `make setup`, `make lint`, and `make test` (PowerShell: use the equivalent commands from `scripts/quality.ps1`).
4. Run `docker compose -f docker-compose.local.yml up -d --build`.
5. Open `http://localhost:5678`, create the local n8n owner, and import JSON from `n8n/workflows`.

No live provider credential is needed for tests. Never commit `.env`.

## Publication gates

Publication is rejected unless the Reel has no unsupported claims, verification exceeds the configured threshold, ffprobe validation passes, an authorised human approves an unexpired callback, and the package has not already been published.

See `MANUAL_ACTIONS_REQUIRED.md` before any external deployment.

