#! /bin/bash

set +e

for dir in proxy store_service postgresql auth_service ; do
  set +e
  # shellcheck disable=SC1090
  . envs/$dir.sh
  set +e
  docker-compose -f ../$dir/docker-compose.yml down --rmi local --remove-orphans
  docker-compose -f ../$dir/docker-compose.dev.yml down --rmi local --remove-orphans
  IMAGE=""${DOCKER_USER}/${APP_NAME}:${APP_VERSION:-latest}""
  echo "$IMAGE"
  set +e
  docker rmi --force "${IMAGE}"
done

docker builder prune -f

set -e

cd ../scripts
