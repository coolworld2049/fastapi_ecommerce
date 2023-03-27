#! /bin/bash

set -e

# shellcheck disable=SC2046
export $(grep -v '^#' ../store_service/.env | xargs)
# shellcheck disable=SC2046
export $(grep -v '^#' ../.env | xargs)
