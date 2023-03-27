#! /bin/bash

set -e

start=$SECONDS

# shellcheck disable=SC2046
export $(grep -v '^#' ../.env | xargs)

echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USER}" --password-stdin

for dir in auth_service store_service proxy; do
  # shellcheck disable=SC1090
  . envs/$dir.sh
  IMAGE=""${DOCKER_USER}/${APP_NAME}:${APP_VERSION:-latest}""
  docker build --no-cache -t "${IMAGE}" ../$dir/
  docker push "${IMAGE}"
  echo "✅   $IMAGE"
done

printf "\n"

echo "✅   " builded and pushed to registry in $((SECONDS - start)) sec
