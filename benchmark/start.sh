#! /bin/bash

set -e

SCRIPTDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source ../.env ../src/.env.auth_service


cd ../src/auth_service/postgresql
docker-compose -f docker-compose.yml up -d --scale slave="$POSTGRESQL_NUM_SLAVES"
cd "$SCRIPTDIR"

echo "run vm"
docker-compose run -d \
  -e APP_ENV="$APP_ENV" \
  -e POSTGRESQL_USERNAME="$POSTGRESQL_USERNAME" \
  -e POSTGRESQL_PASSWORD="$POSTGRESQL_PASSWORD" \
  -e POSTGRESQL_MASTER_HOST="$POSTGRESQL_MASTER_HOST" \
  -e POSTGRESQL_MASTER_PORT="$POSTGRESQL_MASTER_PORT" \
  -e POSTGRESQL_SLAVE_HOST="$POSTGRESQL_SLAVE_HOST" \
  -e POSTGRESQL_SLAVE_PORT="$POSTGRESQL_SLAVE_PORT" \
  -e POSTGRESQL_NUM_SLAVES="$POSTGRESQL_NUM_SLAVES" \
  -e POSTGRESQL_DATABASE="$POSTGRESQL_DATABASE" \
  --name vm vm bash

docker volume prune -f
