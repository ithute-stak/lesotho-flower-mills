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
# Never inherit an implicit production Compose file or project override.
if [[ -n "${COMPOSE_FILE:-}" || -n "${COMPOSE_ENV_FILES:-}" || -n "${COMPOSE_PROFILES:-}" ]]; then
  echo "Unset COMPOSE_FILE, COMPOSE_ENV_FILES and COMPOSE_PROFILES for isolated staging" >&2
  exit 1
fi
bash deploy/staging_preflight.sh
# Start private services only, without public HTTPS edge. Base Compose binds host ports to loopback.
# Do not expose staging over the Internet until TLS/DNS/firewall access has been separately approved.
docker compose -p "$COMPOSE_PROJECT_NAME" -f compose.yaml -f compose.production.yaml -f compose.https.yaml up -d --build db api customer-web driver-web
docker compose -p "$COMPOSE_PROJECT_NAME" -f compose.yaml -f compose.production.yaml -f compose.https.yaml ps
# Validate the application, not merely container creation.
healthy=0
for attempt in $(seq 1 24); do
  if docker compose -p "$COMPOSE_PROJECT_NAME" -f compose.yaml -f compose.production.yaml -f compose.https.yaml \
    exec -T api python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=3)" >/dev/null 2>&1; then
    healthy=1
    break
  fi
  sleep 5
done
if [[ "$healthy" != 1 ]]; then
  echo "FAIL: staging API failed its HTTP health check; deployment not validated" >&2
  docker compose -p "$COMPOSE_PROJECT_NAME" -f compose.yaml -f compose.production.yaml -f compose.https.yaml logs --no-color --tail=100 api db >&2
  exit 1
fi
echo "PASS: restricted staging API health check"
echo "Staging containers requested; verify health, firewall, data isolation and logs. No public staging endpoint has been deployed."
