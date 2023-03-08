#! /bin/bash -x

set -e

docker-compose exec router01 mongosh --port 27017 --eval 'sh.status()'

docker exec -it shard-01-node-a bash -c "echo 'rs.status()' | mongosh --port 27017"
docker exec -it shard-02-node-a bash -c "echo 'rs.status()' | mongosh --port 27017"
