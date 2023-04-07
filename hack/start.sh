#! /bin/bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

docker-compose -f ../fastapi-ecommerce/docker-compose.yml up -d \
  --scale auth_service=0 --scale store_service=0 --scale proxy_service=0

. ../src/store_service/mongodb/init.sh

. ../src/store_service/mongodb/shard.sh

. ../src/proxy_service/mkcert.sh

docker-compose -f ../fastapi-ecommerce/docker-compose.yml up -d

log "$(docker ps)"

log "$(docker stats --no-stream)"

. netcat.sh
