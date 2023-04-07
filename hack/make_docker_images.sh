#! /bin/bash

set -euo pipefail

start=$SECONDS
pushed_images=()

log() { printf '\n%s\n' "$1" >&2; }

source ../.env

echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USER}" --password-stdin

for dir in ../src/*; do
  if [[ -f "$dir/Dockerfile" ]]; then
    service_name="$(basename "${dir}")"
    image="${DOCKER_USER}"/"$service_name":${TAG:-latest}
    log "Building: ${image}"
    docker build -t "${image}" ../src/"$dir"
    log "Pushing: ${image}"
    docker push "${image}"
    declare info
    if [ $? -eq 0 ]; then
      info="✅ $image"
    else
      info="❌ $image"
    fi
    pushed_images+=("$info")
  fi
done

log "$(printf '%s\n' "${pushed_images[@]}")"

log "✔️✔️✔️ Successfully built and pushed all images in $(((SECONDS - start))) sec ✔️✔️✔️ "
