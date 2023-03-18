#! /bin/bash -x

set -e

cd ./auth_service
docker-compose up -d --scale auth_service=0 --scale grafana=0
cd ..

sleep 10

cd ./store_service
docker-compose up -d --scale store_service=0
chmod +x ./scripts/mongodb/init_cluster.sh
. ./scripts/mongodb/init_cluster.sh
cd ..


sleep 10

cd ./proxy
docker-compose up -d
cd ..