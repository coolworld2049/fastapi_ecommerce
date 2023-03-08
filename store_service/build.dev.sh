#! /usr/bin/env bash

set -e

cd ./mongodb_cluster/dev

docker-compose -f docker-compose.yml up -d

. init.sh

cd ..
cd ..

docker-compose -f docker-compose.dev.yml up -d
