sh.addShardToZone("rs-shard-01", "HI_RAM")
sh.addShardToZone("rs-shard-03", "HI_RAM")
sh.addShardToZone("rs-shard-02", "FLASH")
sh.addShardToZone("rs-shard-03", "FLASH")

sh.updateZoneKeyRange("app.Category", { name : MinKey }, { name : MaxKey }, "FLASH" )
sh.updateZoneKeyRange("app.Product", { title : MinKey, category_id: MinKey }, { title : MaxKey, category_id: MaxKey  }, "FLASH" )
sh.updateZoneKeyRange("app.Order", { _id : MinKey }, { _id : MaxKey }, "HI_RAM" )
sh.updateZoneKeyRange("app.OrderProduct", { _id : MinKey }, { _id : MaxKey }, "HI_RAM" )

sh.shardCollection("app.Category", { name: 1 }, true )
sh.shardCollection("app.Product", { title: 1, category_id: 1 }, true )
sh.shardCollection("app.Order", { _id: 1 }, true )
sh.shardCollection("app.OrderProduct", { _id: 1 }, true )

sh.status()