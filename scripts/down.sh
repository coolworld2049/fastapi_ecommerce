#! /bin/bash

set -e

# required $RMI

if [ "$RMI" == true ]; then
    set +e
    rm -R ../src/.volumes
    printf '%s\n' "../src/.volumes --> removed"
  fi

for dir in ../src/*; do
  . export_envs.sh
  export SERVICE_PATH=$dir
  set +e
  docker-compose -f "$dir"/docker-compose.yml down --rmi local --remove-orphans
  if [ -f "$dir"/docker-compose.dev.yml ]; then
    docker-compose -f "$dir"/docker-compose.dev.yml down --rmi local --remove-orphans
  fi
  IMAGE=""${DOCKER_USER}/${APP_NAME}:${APP_VERSION:-latest}""
  printf '%s\n' "$IMAGE"
  if [ "$RMI" == true ]; then
    set +e
    docker rmi --force "${IMAGE}"
    printf '%s\n' "${IMAGE} --> removed"
  fi
  printf '\n'
done

set -e
