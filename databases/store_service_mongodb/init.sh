#! /usr/bin/env bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

until
  docker exec store_service_configsvr01 sh -c "mongosh < /scripts/init-configserver.js"
  docker exec store_service_shard01_a sh -c "mongosh < /scripts/init-shard01.js"
  docker exec store_service_shard02_a sh -c "mongosh < /scripts/init-shard02.js"
  docker exec store_service_shard03_a sh -c "mongosh < /scripts/init-shard03.js"
  docker exec store_service_router01 sh -c "mongosh < /scripts/init-router.js"
do
  log "sleep 5 sec and try again"
  sleep 5
done
