#! /bin/bash

set -e

cd ./proxy
docker-compose down --rmi all --remove-orphans
cd ..

cd ./store_service
docker-compose down --rmi all --remove-orphans
cd ..

cd ./auth_service
docker-compose down --rmi all --remove-orphans
cd ..
