#! /usr/bin/env bash

set -euo pipefail

#rs-shard-01 HI_RAM
#rs-shard-02 FLASH
#rs-shard-03 HI_RAM and FLASH

#HI_RAM
#Servers with high memory capacity.
#Collections requiring more memory, such as collections with large indexes, should be on the HI_RAM shards.

#FLASH
#Servers with flash drives for fast storage speeds.
#Large collections requiring fast data retrieval should be on the FLASH shards.

docker exec store_service_router01 mongosh --port 27017 --eval '[
sh.addShardToZone("rs-shard-01", "HI_RAM"),
sh.addShardToZone("rs-shard-03", "HI_RAM"),
sh.addShardToZone("rs-shard-02", "FLASH"),
sh.addShardToZone("rs-shard-03", "FLASH"),

sh.updateZoneKeyRange("app.Category", { name : MinKey }, { name : MaxKey }, "FLASH" ),
sh.updateZoneKeyRange("app.Product", { title : MinKey, category_id: MinKey }, { title : MaxKey, category_id: MaxKey  }, "FLASH" ),
sh.updateZoneKeyRange("app.Order", { _id : MinKey }, { _id : MaxKey }, "HI_RAM" ),
sh.updateZoneKeyRange("app.OrderProduct", { _id : MinKey }, { _id : MaxKey }, "HI_RAM" ),

sh.shardCollection("app.Category", { name: 1 }, true ),
sh.shardCollection("app.Product", { title: 1, category_id: 1 }, true ),
sh.shardCollection("app.Order", { _id: 1 }, true ),
sh.shardCollection("app.OrderProduct", { _id: 1 }, true ),

sh.status()
]'
