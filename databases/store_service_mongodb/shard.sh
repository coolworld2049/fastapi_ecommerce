#! /usr/bin/env bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

#rs-shard-01 HI_RAM
#rs-shard-02 FLASH
#rs-shard-03 HI_RAM and FLASH

until
  docker exec store_service_mongodb_router01 mongosh --port 27017 --eval '[
    sh.addShardToZone("rs-shard-01", "HI_RAM"),
    sh.addShardToZone("rs-shard-03", "HI_RAM"),
    sh.addShardToZone("rs-shard-02", "FLASH"),
    sh.addShardToZone("rs-shard-03", "FLASH"),

    sh.updateZoneKeyRange("app.Category", { name : MinKey }, { name : MaxKey }, "FLASH" ),
    sh.updateZoneKeyRange("app.Product", { title : MinKey, category_id: MinKey }, { title : MaxKey, category_id: MaxKey  }, "FLASH" ),
    sh.updateZoneKeyRange("app.Order", { _id : MinKey }, { _id : MaxKey }, "HI_RAM" ),
    sh.updateZoneKeyRange("app.OrderProduct", { _id : MinKey }, { _id : MaxKey }, "HI_RAM" ),

    sh.shardCollection("app.Category", { name: source_db }, true ),
    sh.shardCollection("app.Product", { title: source_db, category_id: source_db }, true ),
    sh.shardCollection("app.Order", { _id: source_db }, true ),
    sh.shardCollection("app.OrderProduct", { _id: source_db }, true ),

    sh.status()
    ]'
do
  log "sleep 5 sec and try again"
  sleep 5
done
