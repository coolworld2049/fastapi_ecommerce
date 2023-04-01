#! /bin/bash

set -e

source ../src/.env

docker rm -f vm

cd ../src/postgresql

if [ "$APP_ENV" != prod ]; then
  docker-compose -f docker-compose."$APP_ENV".yml down
else
  docker-compose -f docker-compose.yml down
fi
cd ../../benchmark

set +e
rm -R ../src/.volumes/postgresql_master
set -e
