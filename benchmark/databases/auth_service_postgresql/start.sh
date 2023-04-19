#! /usr/bin/env bash

log() { printf '\n%s\n' "$1" >&2; }

rel_path=../../../

source $rel_path/databases/auth_service_postgresql/.env

# shellcheck disable=SC2046
export $(grep -v '^#' $rel_path.env | xargs -d '\n')

image=benchmark_auth_service_postgresql

docker build -t $image .

docker run -itd \
  -e STAGE="$STAGE" \
  -e POSTGRESQL_USERNAME="$POSTGRESQL_USERNAME" \
  -e POSTGRESQL_DATABASE="$POSTGRESQL_DATABASE" \
  -e POSTGRESQL_MASTER_HOST=auth_service_pgbouncer_master \
  -e POSTGRESQL_MASTER_PORT=6432 \
  -e POSTGRESQL_REPLICA_HOST=auth_service_pgbouncer_replica_01 \
  -e POSTGRESQL_REPLICA_PORT=6432 \
  -e WRITE_TX_MULTIPLIER=2 \
  -e WRITE_CLIENT_MULTIPLIER=1 \
  -e READ_TX_MULTIPLIER=2 \
  -e READ_CLIENT_MULTIPLIER=1 \
  --name $image \
  --mount type=bind,src="$PWD"/pgbench,dst=/pgbench \
  --network fastapi-ecommerce_default \
  $image bash
