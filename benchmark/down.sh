#! /usr/bin/env bash

set -e

SCRIPTDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

docker rm -f benchmark_vm

cd ../src/auth_service/postgresql
docker-compose -p benchmark_postgresql down
cd "$SCRIPTDIR"

docker volume prune -f --filter "label=keep"