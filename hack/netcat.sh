#! /usr/bin/env bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

source ../.env

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

PORTS=(27122-27130 27017 27119 6432 6434-6435 5432 5434-5435 443 80)

for port in "${PORTS[@]}"; do
  set +e
  url="127.0.0.1"
  CMD="$(nc -vz $url "$port")"
  if [ $? -eq 1 ]; then
    printf '%s' "$CMD"
    exit 1
  else
    printf '%s' "$CMD"
  fi
done
