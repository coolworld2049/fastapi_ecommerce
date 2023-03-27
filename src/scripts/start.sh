#! /bin/bash

set -e

. envs/auth_service.sh
cd ../auth_service
docker-compose up -d --no-build \
  --scale auth_service=0
cd ../postgresql
docker-compose up -d \
  --scale slave="${POSTGRESQL_NUM_SLAVES}" \
  --scale pgbouncer_slave="${PGBOUNCER_NUM_SLAVES}"
sleep 10
cd ../auth_service
docker-compose up -d --no-build
docker-compose restart auth_service
cd ../scripts

. envs/store_service.sh
cd ../store_service
docker-compose up -d --no-build
cd scripts/mongodb
. init_cluster.sh
sleep 10
cd ../../../scripts

. envs/proxy.sh
cd ../proxy
. ./mkcert.sh
docker-compose up -d --no-build

cd ../scripts

docker volume prune -f --filter "label!=keep"
