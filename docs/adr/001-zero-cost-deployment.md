# ADR-001: Zero-cost deployment profile

- Status: Accepted
- Date: 2026-08-05

## Context

The supplied requirements describe both Cloud Run hosting/render jobs and a later zero-cost design using an eligible Compute Engine e2-micro plus GitHub Actions. Scale-to-zero n8n is operationally awkward because n8n must receive callbacks and its free-cost behavior is less predictable when paired with managed networking and secrets.

## Decision

The owner has exhausted Google Cloud free-tier eligibility. Use an always-on machine the owner already controls for n8n, expose only its loopback service through Tailscale Funnel HTTPS, and use GitHub Actions for FFmpeg rendering. Use SQLite locally and PostgreSQL/Supabase through SQLAlchemy. Google Cloud and Cloud Run are removed from the active deployment profile.

## Consequences

- The host must remain powered, awake, patched, and connected; this profile has no cloud-compute SLA.
- Funnel has public bandwidth limits and only uses the tailnet's `*.ts.net` hostname.
- Rendering never competes with n8n for the host because it runs in GitHub Actions.
- GitHub Actions minutes and Cloudinary retention require hard quotas.
- No router port-forward or purchased domain is required.
