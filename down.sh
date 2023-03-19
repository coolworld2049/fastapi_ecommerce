#! /bin/bash -x

set -e

cd ./proxy
docker-compose down --rmi local --remove-orphans
cd ..

cd ./store_service
docker-compose down --rmi local --remove-orphans
cd ..

cd ./auth_service
docker-compose down --rmi local --remove-orphans
cd ..

set +e

. ./test.sh