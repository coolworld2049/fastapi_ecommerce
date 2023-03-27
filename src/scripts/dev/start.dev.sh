#! /bin/bash

set -e

cd ..

. envs/auth_service.sh
cd ../auth_service
docker-compose up -d --no-build --scale auth_service=0
cd ../postgresql
export POSTGRESQL_NUM_SLAVES=1
export POSTGRESQL_NUM_SYNCHRONOUS_REPLICAS=1
docker-compose -f docker-compose.dev.yml up -d
cd ../scripts

. envs/store_service.sh
cd ../store_service
docker-compose up -d --no-build --scale store_service=0
cd ../mongodb
docker-compose up -d
sleep 5
. init_cluster.sh
cd ../scripts

cd envs

docker volume prune -f --filter "label!=keep"
