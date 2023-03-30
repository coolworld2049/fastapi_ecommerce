#! /bin/bash

set -e

export ROOT_PATH=../src

source $ROOT_PATH/.env

printf '\n%s\n\n' "❗ APP_ENV=$APP_ENV"

export RMI="${RMI:-true}" RMV="${RMV:-false}"

if [ "$APP_ENV" != prod ]; then
  export RMI=true RMV=true
fi

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
    printf '%s\n' "${IMAGE} --> remove image"
    docker rmi --force "${IMAGE}"
  fi
  printf '\n'
done

if [ "$RMV" == true ]; then
  set +e
  printf '%s\n' "../src/.volumes/* --> remove volumes"
  rm -R ../src/.volumes
fi
