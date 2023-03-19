#! /bin/bash

set -e

cd ./auth_service
docker-compose up -d
cd ..
sleep 10

cd ./store_service
docker-compose up -d
chmod +x ./scripts/mongodb/init_cluster.sh
. ./scripts/mongodb/init_cluster.sh
cd ..
sleep 10

cd ./proxy
chmod +x mkcert.sh
. ./mkcert.sh
docker-compose up -d

cd ..

docker volume prune --filter "label!=keep" -f
