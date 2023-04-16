#! /usr/bin/env bash

set -e

compose_f=../src/databases/auth_service_postgresql
docker-compose -f $compose_f -p benchmark_postgresql up -d


echo "run benchmark_vm"
docker-compose run -d \
  -e POSTGRESQL_USERNAME="$POSTGRESQL_USERNAME" \
  -e POSTGRESQL_PASSWORD="$POSTGRESQL_PASSWORD" \
  -e POSTGRESQL_DATABASE="$POSTGRESQL_DATABASE" \
  -e POSTGRESQL_MASTER_HOST="$POSTGRESQL_MASTER_HOST" \
  -e POSTGRESQL_MASTER_PORT="$POSTGRESQL_MASTER_PORT" \
  -e POSTGRESQL_REPLICA_HOSTS="$POSTGRESQL_REPLICA_HOSTS" \
  -e POSTGRESQL_NUM_REPLICAS=2 \
  --name benchmark_vm benchmark_vm bash
