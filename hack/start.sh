#! /bin/bash

set -euo pipefail

docker-compose -f ../deploy/docker-compose.yml up -d --no-build

. ../src/mongodb/configure_shards.sh

. ../src/proxy/mkcert.sh

docker volume prune -f --filter "label!=keep"

docker stats --no-stream

. netcat.sh
