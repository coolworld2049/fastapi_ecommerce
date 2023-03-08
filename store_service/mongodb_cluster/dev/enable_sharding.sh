#! /usr/bin/env bash

set -e

docker-compose exec router01 mongosh --port 27017 --eval 'sh.enableSharding("app")'

#docker-compose exec router01 mongosh --port 27017 --eval '
#sh.enableSharding("app"),
#db.adminCommand( { shardCollection: "app.Category", key: { _id: 1} } ),
#db.adminCommand( { shardCollection: "app.Order", key: { _id: 1 } } ),
#db.adminCommand( { shardCollection: "app.OrderProduct", key: { _id: 1 } } ),
#db.adminCommand( { shardCollection: "app.Product", key: { _id: 1 } } ),
#db.adminCommand( { shardCollection: "app.User", key: { _id: 1 } } )
#'
