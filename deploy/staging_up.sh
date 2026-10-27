#!/usr/bin/env bash
# Explicit operator-run deployment for an isolated STAGING host only.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ "${1:-}" != "--deploy-staging" ]]; then
  echo "Usage: bash deploy/staging_up.sh --deploy-staging" >&2
  echo "No changes made. Restricted staging requires explicit operator intent." >&2
  exit 2
fi
if [[ "${LFM_STAGING_APPROVED:-}" != "yes" ]]; then
  echo "Set LFM_STAGING_APPROVED=yes only after reviewing staging isolation and access." >&2
  exit 1
fi
if [[ ! "${COMPOSE_PROJECT_NAME:-}" =~ ^lfm-staging-[a-z0-9][a-z0-9_-]{2,30}$ ]]; then
  echo "COMPOSE_PROJECT_NAME must match lfm-staging-<unique-name> (3-31 safe characters)." >&2
  exit 1
fi
bash deploy/staging_preflight.sh
# Start private services only, without public HTTPS edge. Base Compose binds host ports to loopback.
# Do not expose staging over the Internet until TLS/DNS/firewall access has been separately approved.
docker compose -p "$COMPOSE_PROJECT_NAME" -f compose.yaml -f compose.production.yaml -f compose.https.yaml up -d --build db api customer-web driver-web
docker compose -p "$COMPOSE_PROJECT_NAME" -f compose.yaml -f compose.production.yaml -f compose.https.yaml ps
echo "Staging containers requested; verify health, firewall, data isolation and logs. No public staging endpoint has been deployed."
