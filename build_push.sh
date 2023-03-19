#! /bin/bash

set -e

# shellcheck disable=SC2046
export $(grep -v '^#' .env | xargs)

source .env

docker build -t "${AUTH_SERVICE_IMAGE}" ./auth_service
# shellcheck disable=SC2086
echo "${DOCKER_PASSWORD}" | docker login -u ${DOCKER_USER} --password-stdin
# shellcheck disable=SC2086
docker push ${AUTH_SERVICE_IMAGE}

# shellcheck disable=SC2086
docker build -t ${STORE_SERVICE_IMAGE} ./store_service
# shellcheck disable=SC2086
echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USER} --password-stdin
docker push "${STORE_SERVICE_IMAGE}"

# shellcheck disable=SC2086
docker build -t ${PROXY_IMAGE} ./proxy
# shellcheck disable=SC2086
echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USER} --password-stdin
# shellcheck disable=SC2086
docker push ${PROXY_IMAGE}