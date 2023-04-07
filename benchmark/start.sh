#! /usr/bin/env bash

set -e

SCRIPTDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source ../src/auth_service/.env.prod ../src/auth_service/.env

cd ../src/auth_service/postgresql
docker-compose -p benchmark_postgresql  up -d
cd "$SCRIPTDIR"

POSTGRESQL_REPLICA_HOST=auth_service_pgbouncer_replica_01
POSTGRESQL_REPLICA_PORT=6432

echo "run benchmark_vm"
docker-compose run -d \
  -e POSTGRESQL_USERNAME="$POSTGRESQL_USERNAME" \
  -e POSTGRESQL_PASSWORD="$POSTGRESQL_PASSWORD" \
  -e POSTGRESQL_MASTER_HOST="$POSTGRESQL_MASTER_HOST" \
  -e POSTGRESQL_MASTER_PORT="$POSTGRESQL_MASTER_PORT" \
  -e POSTGRESQL_REPLICA_HOST="$POSTGRESQL_REPLICA_HOST" \
  -e POSTGRESQL_REPLICA_PORT="$POSTGRESQL_REPLICA_PORT" \
  -e POSTGRESQL_NUM_REPLICAS=2 \
  -e POSTGRESQL_DATABASE="$POSTGRESQL_DATABASE" \
  --name benchmark_vm benchmark_vm bash
