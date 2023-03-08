#! /bin/bash -x

set -e

cd ..
cd ./mongodb

docker-compose -f docker-compose.yml up -d

. local.sh

. remote.sh

cd ..

docker-compose -f docker-compose.yml up -d --force-recreate
