#! /bin/bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

docker-compose -f ../deploy/docker-compose.yml down --rmi local --remove-orphans

docker rmi -f \
  coolworldocker/auth_service:latest \
  coolworldocker/proxy:latest \
  coolworldocker/store_service:latest

log "✔️✔️✔️ Successfully down all containers ✔️✔️✔️ "
