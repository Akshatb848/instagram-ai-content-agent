# Zero-cost deployment

Google Cloud is not used. The supported deployment runs Docker on an always-on machine already owned by the operator and exposes n8n through Tailscale Funnel HTTPS. GitHub Actions supplies burst video compute; Supabase supplies PostgreSQL.

Follow `EXTERNAL_SETUP.md`, Phase B, for installation, HTTPS, reboot verification, and rollback. This profile has no mandatory compute charge but no cloud SLA: power, ISP, host, Docker, or Tailscale downtime stops callbacks.

The previous `infra/gce` files are retained only as historical reference and must not be deployed under the zero-cost profile.
