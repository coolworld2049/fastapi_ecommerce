#! /bin/bash

set -e

SCRIPTDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source ../.env

docker rm -f vm

cd ../src/postgresql
docker-compose -f docker-compose.yml down
cd "$SCRIPTDIR"
set +e && rm -R ../src/.volumes/postgresql_master
