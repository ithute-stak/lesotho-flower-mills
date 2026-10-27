#!/usr/bin/env bash
# Preflight for a restricted, non-production LFM staging host.
set -euo pipefail
: "${POSTGRES_DB:?}"
: "${POSTGRES_USER:?}"
: "${POSTGRES_PASSWORD:?}"
: "${DATABASE_URL:?}"
: "${AUTH_SECRET:?}"
: "${ACME_EMAIL:?}"
: "${LFM_CUSTOMER_DOMAIN:?}"
: "${LFM_ADMIN_DOMAIN:?}"
: "${LFM_WAREHOUSE_DOMAIN:?}"
: "${LFM_DRIVER_DOMAIN:?}"

if [[ "${LFM_ENV:-}" == "production" ]]; then
  echo "Refusing restricted staging preflight in production mode" >&2
  exit 1
fi
for flag in LFM_SANDBOX_PAYMENTS_ENABLED LFM_ITHUTE_PAY_CHECKOUT_ENABLED LFM_E2E_SEED; do
  value="${!flag:-false}"
  if [[ "$value" != "false" ]]; then
    echo "Staging safety failure: $flag must be false" >&2
    exit 1
  fi
done
if [[ "$DATABASE_URL" == *localhost* ]]; then
  echo "DATABASE_URL must point to the Compose db service" >&2
  exit 1
fi
docker compose -f compose.yaml -f compose.production.yaml -f compose.https.yaml config --quiet
echo "PASS: restricted staging environment/Compose preflight (no deployment performed)"
