#! /bin/bash

set -e

docker-compose down
docker-compose up -d --scale worker=10