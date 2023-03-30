#! /bin/bash

set +e

docker-compose exec -T configsvr01 bash -c "mongosh < /scripts/init-configserver.js"
docker-compose exec -T shard01-a bash -c "mongosh < /scripts/init-shard01.js"
docker-compose exec -T shard02-a bash -c "mongosh < /scripts/init-shard02.js"
docker-compose exec -T router01 bash -c "mongosh < /scripts/init-router.js"

docker-compose exec -T router01 mongosh --port 27017 --eval 'sh.enableSharding("app")'
docker-compose exec -T router01 mongosh --port 27017 --eval '
sh.enableSharding("app"),
db.adminCommand( { shardCollection: "app.Order", key: { _id: 1 } } ),
db.adminCommand( { shardCollection: "app.OrderProduct", key: { _id: 1 } } )
'

docker-compose exec -T router01 mongosh --port 27017 --eval 'sh.status()'
docker exec -T shard-01-node-a bash -c "echo 'rs.status()' | mongosh --port 27017"
docker exec -T shard-02-node-a bash -c "echo 'rs.status()' | mongosh --port 27017"

docker-compose exec -T router01 mongosh --port 27017 --eval '
use app,
db.stats(),
db.User.getShardDistribution()
'
docker exec -T  mongo-config-01 bash -c "echo 'rs.status()' | mongosh --port 27017"
#docker exec -T  shard-01-node-a bash -c "echo 'rs.status()' | mongosh --port 27017"
#docker exec -T  shard-01-node-a bash -c "echo 'rs.printReplicationInfo()' | mongosh --port 27017"
#docker exec -T  shard-01-node-a bash -c "echo 'rs.printSecondaryReplicationInfo()' | mongosh --port 27017"
