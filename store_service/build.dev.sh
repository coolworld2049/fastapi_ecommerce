#! /bin/bash -x

set -e

cd ./mongodb

docker-compose -f docker-compose.yml up -d

. init.sh

cd ..

docker-compose -f docker-compose.yml up -d --force-recreate
