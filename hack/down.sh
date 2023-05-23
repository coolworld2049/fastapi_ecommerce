#! /usr/bin/env bash

set +e

log() { printf '\n%s\n' "$1" >&2; }

source ../.env

project_name=${PROJECT_NAME?env PROJECT_NAME required}
compose_file=../deployment/compose/docker-compose.yml

docker-compose -p "$project_name" -f "$compose_file" down --rmi local --remove-orphans

log "✔️ Successfully down all containers "
