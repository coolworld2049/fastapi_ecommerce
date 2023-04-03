#! /bin/bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

docker-compose -f ../fastapi-ecommerce/docker-compose.yml up -d --no-build \
  --scale auth_service=0 --scale store_service=0 --scale proxy_service=0

bash ../src/store_service/mongodb/configure_shards.sh

. ../src/proxy_service/mkcert.sh

log "sleep 5"

sleep 5

docker-compose -f ../fastapi-ecommerce/docker-compose.yml up -d --no-build

docker volume prune -f --filter "label!=keep"

docker stats --no-stream

. netcat.sh
