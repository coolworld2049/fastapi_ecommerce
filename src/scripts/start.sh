#! /bin/bash

set -e

. envs/auth_service.sh
cd ../auth_service
docker-compose up -d --no-build \
  --scale auth_service=0
cd ../postgresql
docker-compose up -d \
  --scale slave="${POSTGRESQL_NUM_SLAVES}"
echo "sleep 10"
sleep 10
cd ../auth_service
docker-compose up -d --no-build
cd ../scripts

. envs/store_service.sh
cd ../store_service
docker-compose up -d --no-build --scale store_service=0
cd ../mongodb
docker-compose up -d
echo "sleep 5"
sleep 5
. init_cluster.sh
echo "sleep 10"
sleep 10
cd ../store_service
docker-compose up -d --no-build
cd ../scripts

. envs/proxy.sh
cd ../proxy
. ./mkcert.sh
docker-compose up -d --no-build

cd ../scripts

docker volume prune -f --filter "label!=keep"
