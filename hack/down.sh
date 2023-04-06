#! /bin/bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

source ../.env

docker-compose -f ../fastapi-ecommerce/docker-compose.yml down --rmi local --remove-orphans

docker rmi -f \
  coolworldocker/auth_service:latest \
  coolworldocker/proxy_service:latest \
  coolworldocker/store_service:latest

log "✔️✔️✔️ Successfully down all containers ✔️✔️✔️ "
