#! /bin/bash -x

set -e

cp .env.example .env

cd ./auth_service
cp .env.example .env
docker-compose up -d
cd ..

sleep 10

cd ./store_service
cp .env.example .env
docker-compose up -d
chmod +x ./scripts/mongodb/init_cluster.sh
. ./scripts/mongodb/init_cluster.sh
cd ..

sleep 10

cd ./proxy
cp .env.example .env
chmod +x mkcert.sh
. ./mkcert.sh
docker-compose up -d

cd ..