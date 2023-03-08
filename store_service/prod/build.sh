#! /bin/bash -x

set -e

docker-compose -f docker-compose.yml up -d --force-recreate
