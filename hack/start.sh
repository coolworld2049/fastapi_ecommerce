#! /bin/bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

set +e
REQUIRED_PKG="netcat"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG | grep "install ok installed")
log "Checking for $REQUIRED_PKG: $PKG_OK"
if [ "" = "$PKG_OK" ]; then
  log "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
  sudo apt-get --yes install "$REQUIRED_PKG"
fi
printf "\n"
set -e

. ../src/proxy_service/mkcert.sh

docker-compose -f ../fastapi-ecommerce/docker-compose.yml up -d \
  --scale auth_service=0 --scale store_service=0 --scale proxy_service=0

. ../src/store_service/mongodb/init.sh

. ../src/store_service/mongodb/shard.sh

docker-compose -f ../fastapi-ecommerce/docker-compose.yml --profile proxy_service up -d

docker volume prune -f --filter "label!=keep"

docker ps

docker stats --no-stream

log "sleep 10"
sleep 10

. netcat.sh
