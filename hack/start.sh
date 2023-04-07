#! /usr/bin/env bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

docker-compose -f ../fastapi-ecommerce/docker-compose.yml up -d \
  --scale auth_service=0 --scale store_service=0 --scale proxy_service=0

until . ../src/store_service/mongodb/init.sh; do
  log "Try again"
  sleep 1
done

until . ../src/store_service/mongodb/shard.sh; do
  log "Try again"
  sleep 1
done

. ../src/proxy_service/init.sh

docker-compose -f ../fastapi-ecommerce/docker-compose.yml up -d

log "$(docker ps)"

docker_container_names="$(docker ps --format '{{.Names}},')"
# shellcheck disable=SC2207
array=($(echo "$docker_container_names" | tr ',' "\n"))
for container in "${array[@]}"; do
  log "$(printf '\e[1;34m%-6s\e[m' "$container")"
  docker logs "$container" -n 5
done

log "$(docker stats --no-stream)"

. netcat.sh
