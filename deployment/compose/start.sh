#! /usr/bin/env bash

set -eo pipefail

source ../../.env

log() { printf '\n%s\n' "$1" >&2; }

function auth_service() {
  docker pull "${DOCKER_USER}"/auth_service:latest
  docker-compose -p "$project_name" -f "$compose_file" up -d auth_service_postgresql_master
  docker-compose -p "$project_name" -f "$compose_file" up --force-recreate -d auth_service
}

function store_service() {
  docker pull "${DOCKER_USER}"/store_service:latest
  docker-compose -p "$project_name" -f "$compose_file" up -d store_service_mongodb_router01
  dir=../../databases/store_service_mongodb
  log "execute $dir/ scripts"
  bash $dir/init.sh
  docker-compose -p "$project_name" -f "$compose_file" up --force-recreate -d store_service
}

function proxy_service() {
  dir=../../src/proxy_service
  log "execute $dir scripts"
  bash $dir/init.sh
  docker-compose -p "$project_name" -f "$compose_file" up -d proxy_service
}

function containers_logs() {
  docker_container_names="$(docker ps --format '{{.Names}},')"
  # shellcheck disable=SC2207
  array=($(echo "$docker_container_names" | tr ',' "\n"))
  for container in "${array[@]}"; do
    log "$(printf '\e[1;34m%-6s\e[m' "$container")"
    docker logs "$container" -n 5
  done
}

function info() {
  docker volume prune -f --filter "label!=keep"
  log "$(docker ps)"
  log "$(docker stats --no-stream)"
}

function main() {

  project_name=${PROJECT_NAME?env PROJECT_NAME required}
  compose_file=docker-compose.yml

  start=$SECONDS
  auth_service
  store_service
  proxy_service
  containers_logs
  stop=$SECONDS

  info
  bash health.sh

  log "✔️ Successfully started in $((stop - start)) sec "
}

main
