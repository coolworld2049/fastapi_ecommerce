#! /bin/bash -x

docker exec store_service_router01 mongosh --port 27017 --eval '[
  db.getSiblingDB("app").stats(),
  db.getSiblingDB("app").printShardingStatus(),
  //Category
  db.getSiblingDB("app").Category.getShardDistribution(),
  //Product
  db.getSiblingDB("app").Product.getShardDistribution(),
  //Order
  db.getSiblingDB("app").Order.getShardDistribution(),
  //OrderProduct
  db.getSiblingDB("app").OrderProduct.getShardDistribution(),
]'

docker exec store_service_shard01_a bash -c "echo 'rs.status()' | mongosh --port 27017"
docker exec store_service_shard02_a bash -c "echo 'rs.status()' | mongosh --port 27017"
docker exec store_service_shard03_a bash -c "echo 'rs.status()' | mongosh --port 27017"
