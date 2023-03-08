#! /bin/bash -x

set -e

cd ..
cd ./mongodb

docker-compose -f docker-compose.yml up -d

. local.sh

cd ..

docker-compose -f docker-compose.dev.yml up -d --force-recreate
