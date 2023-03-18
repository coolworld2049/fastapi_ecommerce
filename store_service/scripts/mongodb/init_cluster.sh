#! /bin/bash -x

set +e

docker-compose exec configsvr01 sh -c "mongosh < /scripts/init-configserver.js"
docker-compose exec shard01-a sh -c "mongosh < /scripts/init-shard01.js"
docker-compose exec shard02-a sh -c "mongosh < /scripts/init-shard02.js"
docker-compose exec router01 sh -c "mongosh < /scripts/init-router.js"

docker-compose exec router01 mongosh --port 27017 --eval 'sh.enableSharding("app")'
docker-compose exec router01 mongosh --port 27017 --eval '
sh.enableSharding("app"),
db.adminCommand( { shardCollection: "app.Order", key: { _id: 1 } } ),
db.adminCommand( { shardCollection: "app.OrderProduct", key: { _id: 1 } } )
'

docker-compose exec router01 mongosh --port 27017 --eval 'sh.status()'
docker exec shard-01-node-a bash -c "echo 'rs.status()' | mongosh --port 27017"
docker exec shard-02-node-a bash -c "echo 'rs.status()' | mongosh --port 27017"

#docker-compose exec router01 mongosh --port 27017 --eval '
#use app,
#db.stats(),
#db.User.getShardDistribution()
#'
#docker exec  mongo-config-01 bash -c "echo 'rs.status()' | mongosh --port 27017"
#docker exec  shard-01-node-a bash -c "echo 'rs.status()' | mongosh --port 27017"
#docker exec  shard-01-node-a bash -c "echo 'rs.printReplicationInfo()' | mongosh --port 27017"
#docker exec  shard-01-node-a bash -c "echo 'rs.printSecondaryReplicationInfo()' | mongosh --port 27017"
