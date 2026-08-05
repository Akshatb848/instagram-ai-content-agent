---
name: deployment-runbook
description: Deploy, verify, back up, restore, upgrade, and roll back this project's n8n stack on an eligible Google Compute Engine e2-micro VM.
---

# Deployment operations

1. Confirm project, region, e2-micro eligibility, disk, budget alerts, DNS, and secret storage before mutation.
2. Use idempotent scripts, pinned images, health checks, memory limits, one-worker concurrency, restart policies, and log rotation.
3. Never deploy rendering workers, Ollama, GPUs, Kubernetes, load balancers, or a large local database on the VM.
4. Take and verify a recoverable backup before upgrade; document the exact previous image for rollback.
5. Verify HTTPS, webhook authentication, database connectivity, resource use, and restore procedure after deployment.

