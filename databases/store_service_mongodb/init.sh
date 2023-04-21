#! /usr/bin/env bash

set -euo pipefail

log_blue() { printf '\n\e[1;34m%-6s\e[m\n' "$1" >&2; }

until
  log_blue "init-configserver"
  docker exec store_service_configsvr01 sh -c "mongosh < /scripts/init-configserver.js"
  log_blue "init-shard01"
  docker exec store_service_shard01_a sh -c "mongosh < /scripts/init-shard01.js"
  log_blue "init-shard02"
  docker exec store_service_shard02_a sh -c "mongosh < /scripts/init-shard02.js"
  log_blue "init-shard03"
  docker exec store_service_shard03_a sh -c "mongosh < /scripts/init-shard03.js"
  log_blue "init-router"
  docker exec store_service_router01 sh -c "mongosh < /scripts/init-router.js"
do
  log_blue "sleep 5 sec and try again"
  sleep 5
done