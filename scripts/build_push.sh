#! /bin/bash

set -e

start=$SECONDS

. export_envs.sh

echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USER}" --password-stdin

PUSHED_IMAGES=()

for dir in ../src/*; do
  if [[ -f "../src/$dir/Dockerfile" ]]; then

    # shellcheck disable=SC1090
    export SERVICE_PATH=$dir
    . export_envs.sh
    IMAGE=""${DOCKER_USER}/${APP_NAME}:${APP_VERSION:-latest}""
    docker build -t "${IMAGE}" ../src/"$dir"/
    docker push "${IMAGE}"
    declare msg
    # shellcheck disable=SC2181
    if [ $? -eq 0 ]; then
      msg="✅ $IMAGE"
    else
      msg="❌ $IMAGE"
    fi
    PUSHED_IMAGES+=("$msg")
    printf "\n"
  fi
done

printf '%s\n' "$(printf '%s\n' "${PUSHED_IMAGES[@]}")"

printf "\n"

echo "✔️✔️✔️ built and pushed in $((SECONDS - start)) sec ✔️✔️✔️"

printf "\n"
