#! /usr/bin/env bash

set -e

docker-compose exec router01 mongosh --port 27017 --eval '
use app,
db.stats(),
db.User.getShardDistribution()
'

docker exec -it mongo-config-01 bash -c "echo 'rs.status()' | mongosh --port 27017"

docker exec -it shard-01-node-a bash -c "echo 'rs.status()' | mongosh --port 27017"
docker exec -it shard-01-node-a bash -c "echo 'rs.printReplicationInfo()' | mongosh --port 27017"
docker exec -it shard-01-node-a bash -c "echo 'rs.printSecondaryReplicationInfo()' | mongosh --port 27017"