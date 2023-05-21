#! /usr/bin/env bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

function login() {
  echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USER}" --password-stdin
}

function build_push() {
  # $1 - microservice dir
  log "Building: ${image}"
  docker build -t "${image}" "$SRC_PATH"/"$1"

  log "Pushing: ${image}"
  docker push "${image}"
}

function main() {
  start=$SECONDS
  SRC_PATH=../src

  source ../.env

  login

  for dir in "$SRC_PATH"/*; do
    if [ -f "$dir/Dockerfile" ]; then
      image="${DOCKER_USER}"/"$(basename "${dir}")":${APP_VERSION:-latest}
      build_push "$dir"
      declare info
      if [ $? -eq 0 ]; then
        info="✅ $image"
      else
        info="❌ $image"
      fi
      log "$info"
    fi
  done

  stop=$((SECONDS - start))

  log "✔️ Successfully built and pushed all images in $stop sec "
}

main
