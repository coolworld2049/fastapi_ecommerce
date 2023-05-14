#! /usr/bin/env bash

set -euo pipefail

start=$SECONDS

log() { printf '\n%s\n' "$1" >&2; }

compose_file=../fastapi-ecommerce/docker-compose.yml

source ../.env

docker-compose -f $compose_file up -d auth_service_postgresql_master

docker-compose -f $compose_file up --force-recreate -d auth_service

docker-compose -f $compose_file up -d store_service_mongodb_router01

dir=../databases/store_service_mongodb
log "execute $dir/ scripts"
bash $dir/init.sh
bash $dir/shard.sh

docker-compose -f $compose_file up --force-recreate -d store_service

dir=../src/proxy_service/
log "execute $dir/ scripts"
bash $dir/init.sh

docker-compose -f $compose_file up -d proxy_service

docker volume prune -f --filter "label!=keep"

stop=$SECONDS

log "$(docker ps)"

docker_container_names="$(docker ps --format '{{.Names}},')"
# shellcheck disable=SC2207
array=($(echo "$docker_container_names" | tr ',' "\n"))
for container in "${array[@]}"; do
  log "$(printf '\e[source_db;34m%-6s\e[m' "$container")"
  docker logs "$container" -n 5
done

log "$(docker stats --no-stream)"

. health.sh

log "✔️✔️✔️ Successfully started in $(((stop - start))) sec ✔️✔️✔️ "
