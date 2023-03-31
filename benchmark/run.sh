#! /bin/bash

set -e

source ../src/.env
docker rm -f vm
docker-compose run \
  -e POSTGRESQL_HOST="$POSTGRESQL_MASTER_HOST" \
  -e POSTGRESQL_PORT="$POSTGRESQL_MASTER_PORT" \
  -e POSTGRESQL_DATABASE="$POSTGRESQL_DATABASE" \
  --name vm vm bash
