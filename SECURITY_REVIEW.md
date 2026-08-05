# Security review

The implemented core fails closed on auto-publish and paid fallback, validates signed expiring callbacks with replay prevention, enforces authorised Telegram users, blocks unsupported claims, prevents duplicate publication, uses argument-array subprocess calls, and includes SSRF/public-IP allowlisting helpers.

No secrets are present in workflow exports or `.env.example`; local development credentials are clearly local-only and bind n8n to loopback. CI includes dependency and secret scanning. The local dependency audit could not query PyPI because of the host TLS trust-chain problem and therefore remains an explicit pending gate, not a pass.

Residual risks before production: n8n workflows need full node implementation/import testing; callback nonce persistence must use PostgreSQL rather than an in-memory set; renderer asset downloads need redirect/MIME/size enforcement at the HTTP adapter; live provider permissions and token rotation need sandbox verification.

