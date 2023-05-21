#! /usr/bin/env bash

set -euo pipefail

log_blue() { printf '\e[1;34m%-6s\e[m' "$1" >&2; }

until
  log_blue "init-configserver"
  docker exec store_service_mongodb_configsvr01 sh -c "mongosh < /scripts/init-configserver.js"
  log_blue "init-shard01"
  docker exec store_service_mongodb_shard01_a sh -c "mongosh < /scripts/init-shard01.js"
  log_blue "init-shard02"
  docker exec store_service_mongodb_shard02_a sh -c "mongosh < /scripts/init-shard02.js"
  log_blue "init-shard03"
  docker exec store_service_mongodb_shard03_a sh -c "mongosh < /scripts/init-shard03.js"
  log_blue "init-router"
  docker exec store_service_mongodb_router01 sh -c "mongosh < /scripts/init-router.js"
  log_blue "init-router-sharding"
  docker exec store_service_mongodb_router01 sh -c "mongosh < /scripts/init-router-sharding.js"
do
  log_blue "sleep 5 sec and try again"
  sleep 5
done
