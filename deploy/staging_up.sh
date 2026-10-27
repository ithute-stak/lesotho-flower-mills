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
if [[ "${COMPOSE_PROJECT_NAME:-}" != lfm-staging* ]]; then
  echo "COMPOSE_PROJECT_NAME must begin lfm-staging to prevent accidental production targeting." >&2
  exit 1
fi
bash deploy/staging_preflight.sh
# Only stage database, API, customer and driver app, plus public HTTPS edge.
# Admin and warehouse are deliberately unavailable on public ingress.
docker compose -p "$COMPOSE_PROJECT_NAME" -f compose.yaml -f compose.production.yaml -f compose.https.yaml up -d --build db api customer-web driver-web edge
docker compose -p "$COMPOSE_PROJECT_NAME" -f compose.yaml -f compose.production.yaml -f compose.https.yaml ps
echo "Staging containers requested; verify TLS, health, firewall, data isolation and logs before testers access the host."
