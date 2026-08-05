# Google VM deployment

## Prerequisites

Confirm an eligible US region, one e2-micro VM, eligible standard persistent disk, no GPU/load balancer, a billing budget alert, Ubuntu LTS, a DNS A/AAAA record, and firewall ingress only for SSH, HTTP, and HTTPS. Store secrets outside Git.

## Deploy

1. Install Docker Engine and the Compose plugin from Docker's official Ubuntu repository.
2. Clone the private repository with a read-only deployment key.
3. In `infra/gce`, create `.env` from the documented variable names and set restrictive permissions.
4. Export `DEPLOY_DOMAIN` and `N8N_ENCRYPTION_KEY` from the secret store, then run `bash deploy.sh`.
5. Verify `docker compose ps`, `curl -fsS https://DOMAIN/healthz`, and `docker stats --no-stream`.

## Backup and restore

Stop n8n briefly, archive the n8n volume and dump PostgreSQL/Supabase using a least-privilege backup role. Encrypt and test the archive. To restore, stop services, restore into a fresh volume/database, start the pinned previous image, and verify workflows and credentials decrypt correctly.

## Upgrade and rollback

Back up first. Pull a reviewed pinned image, start it, and verify health plus a manual mock workflow. If verification fails, restore the prior image tag and backup; never run irreversible database downgrades without a tested restore.

