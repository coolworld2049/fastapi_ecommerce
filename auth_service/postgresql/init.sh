#! /bin/bash -x

set -e

# shellcheck disable=SC2046
# shellcheck disable=SC2002
export $(cat ../.env | xargs)

source ../.env

docker-compose up -d