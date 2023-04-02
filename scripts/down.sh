#! /bin/bash

set -e

export SERVICE_PATH=../src

source $SERVICE_PATH/.env

printf '\n%s\n' "❗ APP_ENV=$APP_ENV"

if [ "$APP_ENV" != dev ]; then
  export RMI=true RMV=false
else
  export RMI=true RMV=true
fi

for dir in "$SERVICE_PATH"/*; do
  set +e
  source "$dir"/.env
  IMAGE=""${DOCKER_USER}/${APP_NAME}:${APP_VERSION:-latest}""
  echo "$IMAGE"
  cd "$dir"
  docker-compose down --rmi local --remove-orphans
  cd ../../scripts
  if [ "$RMI" == true ]; then
    set +e
    printf '%s\n' "❗ remove image"
    docker rmi --force "${IMAGE}"
  fi
  printf '\n'
done

if [ "$RMV" == true ]; then
  set +e
  printf '%s\n' "❗ remove volumes path: $SERVICE_PATH/.volumes/*"
  rm -R .$SERVICE_PATH/.volumes
fi
