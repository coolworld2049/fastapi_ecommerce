#! /bin/bash

set -e

#required boolean $RMI - remove images, $RMV - remove volumes

for dir in ../src/*; do
  set +e
  source "$dir"/.env
  IMAGE=""${DOCKER_USER}/${APP_NAME}:${APP_VERSION:-latest}""
  echo "$IMAGE"
  docker-compose -f "$dir"/docker-compose.yml down --rmi local --remove-orphans
  if [ -f "$dir"/docker-compose.dev.yml ]; then
    docker-compose -f "$dir"/docker-compose.dev.yml down --rmi local --remove-orphans
  fi
  if [ "$RMI" == true ]; then
    set +e
    printf '%s\n' "${IMAGE} --> remove"
    docker rmi --force "${IMAGE}"
  fi
  printf '\n'
done

if [ "$RMV" == true ]; then
  set +e
  printf '%s\n' "../src/.volumes/* --> remove"
  rm -R ../src/.volumes
fi
