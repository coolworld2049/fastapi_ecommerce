#! /bin/bash -x

set -e

cd ..

docker-compose -f docker-compose.yml up -d --scale store_service=0

sleep 5

cd ./scripts/mongodb

. init.sh

