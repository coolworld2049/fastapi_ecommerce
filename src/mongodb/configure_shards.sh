#! /bin/bash

set -euo pipefail

printf "\n"

docker exec -it mongo-config-01 bash -c -i '
mongosh < /scripts/init-configserver.js > result.json
cat result.json | grep "MongoServerError:"
'

if [ $? -eq 0 ]; then
  exit 1;
fi

docker exec shard-01-node-a bash -c "mongosh < /scripts/init-shard01.js"
docker exec shard-02-node-a bash -c "mongosh < /scripts/init-shard02.js"
docker exec router-01 bash -c "mongosh < /scripts/init-router.js"

docker exec router-01 mongosh --port 27017 --eval 'sh.enableSharding("app")'
docker exec router-01 mongosh --port 27017 --eval '
sh.enableSharding("app"),
db.adminCommand( { shardCollection: "app.Order", key: { _id: 1 } } ),
db.adminCommand( { shardCollection: "app.OrderProduct", key: { _id: 1 } } )
'

docker exec router-01 mongosh --port 27017 --eval 'sh.status()'
#docker exec shard-01-node-a bash -c "echo 'rs.status()' | mongosh --port 27017"
#docker exec shard-01-node-abash -c "echo 'rs.status()' | mongosh --port 27017"

docker exec router-01 mongosh --port 27017 --eval '
use app,
db.stats(),
db.User.getShardDistribution()
'
#docker exec mongo-config-01 bash -c "echo 'rs.status()' | mongosh --port 27017"
#docker exec shard-01-node-a bash -c "echo 'rs.status()' | mongosh --port 27017"
#docker exec shard-01-node-a bash -c "echo 'rs.printReplicationInfo()' | mongosh --port 27017"
#docker exec shard-01-node-a bash -c "echo 'rs.printSecondaryReplicationInfo()' | mongosh --port 27017"

printf "\n"
