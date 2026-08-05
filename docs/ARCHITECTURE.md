# Architecture

The default production profile separates lightweight orchestration from video compute.

```text
GitHub Actions schedule -> signed n8n webhook -> ingestion/ranking/verification
                                              -> Gemini or configured fallback
                                              -> opaque render job -> GitHub Actions + FFmpeg
                                              -> Cloudinary preview -> Telegram approval
                                              -> official Instagram Graph API -> metrics/history

n8n on owner-operated machine + Tailscale Funnel <-> PostgreSQL/Supabase
local development                              <-> SQLite
```

## Trust boundaries

External feeds and media are untrusted. URLs pass scheme, DNS/IP, allowlist, size, MIME, and redirect checks. Retrieved prose is evidence only and never operational instruction. All state-changing callbacks are authenticated, time-bounded, replay-protected, and idempotent. Publishing requires a validated render plus an explicit authorised approval; `AUTO_PUBLISH=false` is the immutable default.

## Cost boundary

The orchestrator uses an always-on machine already owned by the user and a free Tailscale Funnel HTTPS endpoint. Rendering runs only on bounded GitHub Actions jobs. Limits are enforced in application code before provider calls or dispatch. No paid fallback is permitted. See ADR-001 and `EXTERNAL_SETUP.md` for the decision and trade-offs.
