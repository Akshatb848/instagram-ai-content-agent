# ADR-001: Zero-cost deployment profile

- Status: Accepted
- Date: 2026-08-05

## Context

The supplied requirements describe both Cloud Run hosting/render jobs and a later zero-cost design using an eligible Compute Engine e2-micro plus GitHub Actions. Scale-to-zero n8n is operationally awkward because n8n must receive callbacks and its free-cost behavior is less predictable when paired with managed networking and secrets.

## Decision

Use an eligible e2-micro VM for n8n and a lightweight HTTPS proxy. Use GitHub Actions for FFmpeg rendering. Use SQLite locally and PostgreSQL/Supabase in hosted environments through SQLAlchemy. Keep Cloud Run manifests as an optional, independently deployable alternative, not the default free profile.

## Consequences

- The VM must be kept in an eligible region/machine/disk configuration and guarded with billing alerts.
- Rendering never competes with n8n for the VM's limited memory.
- GitHub Actions minutes and Cloudinary retention require hard quotas.
- A public HTTPS endpoint or tunnel is needed for callbacks.

