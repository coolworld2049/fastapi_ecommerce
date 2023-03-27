#! /bin/bash

set +e

export RMI=false

for dir in proxy mongodb store_service postgresql auth_service; do
  set +e
  # shellcheck disable=SC1090
  . envs/$dir.sh
  set +e
  docker-compose -f ../$dir/docker-compose.yml down --rmi local --remove-orphans
  docker-compose -f ../$dir/docker-compose.dev.yml down --rmi local --remove-orphans
  IMAGE=""${DOCKER_USER}/${APP_NAME}:${APP_VERSION:-latest}""
  echo "$IMAGE"
  set +e
  if $RMI; then
    docker rmi --force "${IMAGE}"
  fi
done

set -e

cd ../scripts
