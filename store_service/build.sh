#! /usr/bin/env bash

set -e

cd ./mongodb

docker-compose -f docker-compose.yml up -d

. init.sh

. enable_sharding.sh

. verify.sh

. info.sh

cd ..

docker-compose -f docker-compose.yml up -d
