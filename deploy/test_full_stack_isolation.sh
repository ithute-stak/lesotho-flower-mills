#!/usr/bin/env bash
set -euo pipefail
# Run only in disposable CI. Uses real LFM containers, not synthetic nginx stand-ins.
project="${COMPOSE_PROJECT_NAME:-lfm-stack-isolation}"
files=(-f compose.yaml -f compose.production.yaml -f compose.https.yaml)
cleanup() { docker compose -p "$project" "${files[@]}" down -v --remove-orphans || true; }
trap cleanup EXIT
docker compose -p "$project" "${files[@]}" config --quiet
docker compose -p "$project" "${files[@]}" up -d --build db api customer-web admin-web warehouse-web driver-web
public_network="${project}_public_edge"
edge_networks="$(docker network inspect "$public_network" --format '{{range .Containers}}{{.Name}} {{end}}')"
echo "Public edge members: $edge_networks"
for forbidden in admin-web warehouse-web api db; do
 if echo "$edge_networks" | grep -Eq "(${project}-|${project}_)${forbidden}(-|_| )"; then
  echo "FAIL: $forbidden present on public_edge" >&2
  exit 1
 fi
done
for allowed in customer-web driver-web; do
 if ! echo "$edge_networks" | grep -q "$allowed"; then
  echo "FAIL: $allowed missing from public_edge" >&2
  exit 1
 fi
done
# DNS-level reachability from a disposable peer on exactly the same edge network.
docker run --rm --network "$public_network" curlimages/curl:8.12.1 -fsS --retry 8 --retry-delay 3 --max-time 15 http://customer-web:3000/ >/dev/null
for forbidden in admin-web:3001 warehouse-web:3002 api:8000 db:5432; do
 if docker run --rm --network "$public_network" curlimages/curl:8.12.1 -fsS --connect-timeout 2 --max-time 4 "http://$forbidden/" >/dev/null 2>&1; then
  echo "FAIL: $forbidden directly accessible from public_edge" >&2
  exit 1
 fi
done
echo "PASS: actual LFM public_edge membership and denied DNS reachability"
