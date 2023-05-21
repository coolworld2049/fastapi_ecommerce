#! /usr/bin/env bash

docker exec store_service_mongodb_router01 mongosh --port 27017 --eval '[
  db.getSiblingDB("app").stats(),
  db.getSiblingDB("app").printShardingStatus()
]'

docker exec store_service_mongodb_router01 bash -c "echo 'rs.status()' | mongosh --port 27017"
docker exec store_service_mongodb_configsvr01 bash -c "echo 'rs.status()' | mongosh --port 27017"
docker exec store_service_mongodb_shard01_a bash -c "echo 'rs.status()' | mongosh --port 27017"
docker exec store_service_mongodb_shard02_a bash -c "echo 'rs.status()' | mongosh --port 27017"
docker exec store_service_mongodb_shard03_a bash -c "echo 'rs.status()' | mongosh --port 27017"
