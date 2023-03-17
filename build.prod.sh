#! /bin/bash -x

set -e

cd ./auth_service
docker-compose up -d
cd ..

sleep 15

cd ./store_service
docker-compose up -d
cd ./scripts/mongodb
. ./init_cluster.sh
cd ../../..


sleep 10

cd proxy
. ./mkcert.sh
docker-compose up -d

sleep 5

curl --head http://auth-service.fastapi-ecommerce/docs

curl --head http://store-service.fastapi-ecommerce/docs

cd ..