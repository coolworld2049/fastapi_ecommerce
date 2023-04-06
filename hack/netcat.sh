#! /bin/bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

source ../.env

log "❗ STAGE=$APP_ENV"

PORTS=(27122-27130 27017 27119 6432-6434 5432-5434 443 80)

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
