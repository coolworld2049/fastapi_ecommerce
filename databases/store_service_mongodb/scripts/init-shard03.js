rs.initiate({_id: "rs-shard-03", version: 1, members: [ { _id: 0, host : "store_service_shard03_a:27017" }, { _id: 1, host : "store_service_shard03_b:27017" }, { _id: 2, host : "store_service_shard03_c:27017" } ] })