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
# Probe TCP connections, not HTTP responses: a database or API can accept a
# connection without returning HTTP 2xx, which would fool curl -f.
probe_tcp() {
  local host="$1" port="$2"
  docker run --rm --network "$public_network" \
    -e TARGET_HOST="$host" -e TARGET_PORT="$port" python:3.12-alpine \
    python -c 'import os,socket,sys; h=os.environ["TARGET_HOST"]; p=int(os.environ["TARGET_PORT"]); s=socket.socket(); s.settimeout(3); sys.exit(0 if s.connect_ex((h,p))==0 else 1)' >/dev/null 2>&1
}
for service_port in admin-web:3001 warehouse-web:3002 api:8000 db:5432; do
  service="${service_port%%:*}"
  port="${service_port##*:}"
  # Positive control from the application network: otherwise a stopped
  # service would misleadingly count as an isolation success.
  if ! docker run --rm --network "${project}_default" \
    -e TARGET_HOST="$service" -e TARGET_PORT="$port" python:3.12-alpine \
    python -c 'import os,socket,sys; h=os.environ["TARGET_HOST"]; p=int(os.environ["TARGET_PORT"]); s=socket.socket(); s.settimeout(4); sys.exit(0 if s.connect_ex((h,p))==0 else 1)' >/dev/null 2>&1; then
    echo "FAIL: $service:$port is not reachable from its intended application network" >&2
    exit 1
  fi
  if probe_tcp "$service" "$port"; then
    echo "FAIL: public edge TCP access to $service:$port" >&2
    exit 1
  fi
  container_id="$(docker compose -p "$project" "${files[@]}" ps -q "$service")"
  private_ip="$(docker inspect "$container_id" --format '{{range $name, $network := .NetworkSettings.Networks}}{{if eq $name "'"${project}"'_default"}}{{$network.IPAddress}}{{end}}{{end}}')"
  test -n "$private_ip" || { echo "FAIL: no private IP for $service" >&2; exit 1; }
  if probe_tcp "$private_ip" "$port"; then
    echo "FAIL: public edge TCP access to $service IP $private_ip:$port" >&2
    exit 1
  fi
done
echo "PASS: actual LFM public_edge membership and denied hostname/direct-IP TCP connectivity"
