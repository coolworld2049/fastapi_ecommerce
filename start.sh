#! /bin/bash

set -e

cd ./auth_service
docker-compose up -d
cd ..
sleep 10

cd ./store_service
docker-compose up -d
cd ..
sleep 10

cd ./proxy
. ./mkcert.sh
docker-compose up -d
cd ..