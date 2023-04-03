#! /bin/bash

set -euo pipefail

docker-compose -f ../deploy/docker-compose.yml up -d --no-build

bash ../src/mongodb/configure_shards.sh

. ../src/proxy_service/mkcert.sh

docker volume prune -f --filter "label!=keep"

docker stats --no-stream

. netcat.sh
