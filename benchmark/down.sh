#! /bin/bash

set -e

source ../src/.env

docker rm -f vm

if [ "$APP_ENV" != prod ]; then
  cd ../src/postgresql
  docker-compose -f docker-compose."$APP_ENV".yml down
  cd ../../benchmark
  set +e
  rm -R ../src/.volumes/postgresql_master
  set -e
fi
