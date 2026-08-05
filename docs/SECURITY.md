# Security and threat model

| Threat | Control |
| --- | --- |
| Malicious RSS / prompt injection | Content is data-only, normalized, screened, and placed inside strict structured prompts. |
| SSRF | HTTP(S) only, explicit host allowlists, public-IP resolution, redirect revalidation, MIME/size/time limits. |
| Malicious media | Licensed-source allowlist, content-type and size validation, FFmpeg isolation, no shell interpolation. |
| Callback spoofing/replay | HMAC-SHA256, constant-time verification, expiry, nonce storage, authorised Telegram IDs. |
| GitHub dispatch abuse | Opaque UUID only, least-privilege token, HMAC callback, one-job concurrency. |
| Leaked Meta token | Secret store only, redacted logs, narrow permissions, rotation runbook. |
| Duplicate publication | Database uniqueness plus pre-publish idempotency gate. |
| Copyright infringement | Approved sources only, attribution manifest, reject unknown rights. |
| Hallucinated claims | Primary-source evidence, confidence threshold, unsupported-claim hard block. |

Never pass untrusted text to a shell, expression evaluator, template code context, URL without validation, or publication adapter. Rotate any credential that appears in logs or Git history.

