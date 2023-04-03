#! /bin/bash

set -euo pipefail

start=$SECONDS

COMPOSE_FILE=${COMPOSE_FILE:-env COMPOSE_FILE required}

printf "\n"

docker-compose -f "$COMPOSE_FILE" -T exec store_service_configsvr01 bash -c "mongosh < /scripts/init-configserver.js"
docker-compose -f "$COMPOSE_FILE" -T exec store_service_shard01_a bash -c "mongosh < /scripts/init-shard01.js"
docker-compose -f "$COMPOSE_FILE" -T exec store_service_shard02_a bash -c "mongosh < /scripts/init-shard02.js"
docker-compose -f "$COMPOSE_FILE" -T exec store_service_router01 bash -c "mongosh < /scripts/init-router.js"

docker-compose -f "$COMPOSE_FILE" exec store_service_router01 mongosh --port 27017 --eval 'sh.enableSharding("app")'
docker-compose -f "$COMPOSE_FILE" exec store_service_router01 mongosh --port 27017 --eval '
sh.enableSharding("app"),
db.adminCommand( { shardCollection: "app.Order", key: { _id: 1 } } ),
db.adminCommand( { shardCollection: "app.OrderProduct", key: { _id: 1 } } )
'

docker-compose -f "$COMPOSE_FILE" exec store_service_router01 mongosh --port 27017 --eval 'sh.status()'
#docker-compose -f "$COMPOSE_FILE" -T exec store_service_shard01_a bash -c "echo 'rs.status()' | mongosh --port 27017"
#docker-compose -f "$COMPOSE_FILE" -T exec store_service_shard01_a bash -c "echo 'rs.status()' | mongosh --port 27017"

docker-compose -f "$COMPOSE_FILE" exec store_service_router01 mongosh --port 27017 --eval '
use app,
db.stats(),
db.User.getShardDistribution()
'
#docker-compose -f "$COMPOSE_FILE" -T exec store_service_configsvr01 bash -c "echo 'rs.status()' | mongosh --port 27017"
#docker-compose -f "$COMPOSE_FILE" -T exec store_service_shard01_a bash -c "echo 'rs.status()' | mongosh --port 27017"
#docker-compose -f "$COMPOSE_FILE" -T exec store_service_shard01_a bash -c "echo 'rs.printReplicationInfo()' | mongosh --port 27017"
#docker-compose -f "$COMPOSE_FILE" -T exec store_service_shard01_a bash -c "echo 'rs.printSecondaryReplicationInfo()' | mongosh --port 27017"


printf "\n%s\n" "✔️✔️✔️ Successfully configured shards in $((SECONDS - start)) sec ✔️✔️✔️ "
