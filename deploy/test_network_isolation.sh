#!/usr/bin/env bash
set -euo pipefail
# Disposable runtime smoke of the declared public_edge/default network separation.
# This does NOT launch the full LFM application stack.
prefix="lfm-isolation-${GITHUB_RUN_ID:-local}-$$"
public="${prefix}-public"
private="${prefix}-private"
cleanup() {
  docker rm -f "${prefix}-admin" "${prefix}-customer" >/dev/null 2>&1 || true
  docker network rm "$public" "$private" >/dev/null 2>&1 || true
}
trap cleanup EXIT
docker network create "$public" >/dev/null
docker network create "$private" >/dev/null
docker run -d --name "${prefix}-admin" --network "$private" --network-alias admin-web nginx:1.27-alpine >/dev/null
docker run -d --name "${prefix}-customer" --network "$public" --network-alias customer-web nginx:1.27-alpine >/dev/null
admin_ip="$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "${prefix}-admin")"
# Network peer must be reachable, proving the probe is actually functional.
docker run --rm --network "$public" curlimages/curl:8.12.1 -fsS --max-time 8 http://customer-web/ >/dev/null
# A cross-network connection must fail even when the private IP is known.
if docker run --rm --network "$public" curlimages/curl:8.12.1 -fsS --connect-timeout 2 --max-time 4 "http://$admin_ip/" >/dev/null 2>&1; then
  echo "FAIL: public edge can reach private admin IP" >&2
  exit 1
fi
if docker run --rm --network "$public" curlimages/curl:8.12.1 -fsS --connect-timeout 2 --max-time 4 http://admin-web/ >/dev/null 2>&1; then
  echo "FAIL: public edge can resolve and reach private admin hostname" >&2
  exit 1
fi
echo "PASS: public peer reachable; private admin peer inaccessible via IP and hostname"
