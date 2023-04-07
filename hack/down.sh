#! /bin/bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

source ../.env

docker-compose -f ../fastapi-ecommerce/docker-compose.yml down --rmi local --remove-orphans

docker volume prune -f --filter "label!=keep"

log "✔️✔️✔️ Successfully down all containers ✔️✔️✔️ "
