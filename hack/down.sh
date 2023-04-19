#! /usr/bin/env bash

set +e

log() { printf '\n%s\n' "$1" >&2; }

compose_file=../fastapi-ecommerce/docker-compose.yml

docker-compose -f $compose_file down --rmi local --remove-orphans

log "✔️✔️✔️ Successfully down all containers ✔️✔️✔️ "

log ""