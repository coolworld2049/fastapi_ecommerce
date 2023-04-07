#! /bin/bash

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

log "$(docker stats --no-stream)"

. netcat.sh
