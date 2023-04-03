#! /bin/bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

source ../.env

log "❗ STAGE=$APP_ENV"

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

PORTS=(27122-27127 27017 27119 6433 6434 5432 443 80)

for port in "${PORTS[@]}"; do
  set +e
  url="127.0.0.1"
  CMD="$(nc -vz $url "$port")"
  printf '%s' "$CMD"
done
