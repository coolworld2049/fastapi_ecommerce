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

docker-compose -f ../fastapi-ecommerce/docker-compose.yml up -d --no-build --scale proxy_service=0

. ../src/store_service/mongodb/init.sh

#docker-compose -f ../fastapi-ecommerce/docker-compose.yml exec -T store_service bash <<'EOF'
#log() { printf '\n%s\n' "$1" >&2; }
#attempts=0
#max=10
#url=http://store_service:80/api/v1/ping/auth_service
#while [ $attempts -le $max ]; do
#  resp=$(curl --write-out '%{http_code}' --silent --output /dev/null $url)
#  log "ping store_service: $url attempt: $attempts status_code: $resp"
#  if [ "$resp" == 200 ]; then
#    log "$url success ping"
#    break
#  elif [ "$resp" != 200 ] && [ $attempts -ge $max ]; then
#    log "$url failed ping"
#    exit 1
#  fi
#  log "sleep 5"
#  sleep 5
#  attempts=$((attempts + 1))
#done
#EOF

. ../src/store_service/mongodb/shard.sh

docker-compose -f ../fastapi-ecommerce/docker-compose.yml --profile proxy_service up -d --no-build

docker volume prune -f --filter "label!=keep"

docker stats --no-stream

. netcat.sh
