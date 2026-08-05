#!/usr/bin/env bash
set -euo pipefail
: "${DEPLOY_DOMAIN:?Set DEPLOY_DOMAIN}"
: "${N8N_ENCRYPTION_KEY:?Set N8N_ENCRYPTION_KEY through the secret store}"
command -v docker >/dev/null
test "$(uname -s)" = Linux
docker compose -f infra/gce/docker-compose.yml pull
docker compose -f infra/gce/docker-compose.yml up -d --remove-orphans
docker compose -f infra/gce/docker-compose.yml ps

