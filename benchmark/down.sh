#! /bin/bash

set -e

SCRIPTDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source ../../.env

docker rm -f vm

if [ "$APP_ENV" != prod ]; then
  cd ../src/postgresql
  docker-compose -f docker-compose."$APP_ENV".yml down
  cd "$SCRIPTDIR"
  set +e && rm -R ../.volumes/postgresql_master
fi
