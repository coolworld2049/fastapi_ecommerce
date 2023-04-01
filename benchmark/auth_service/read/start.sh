#! /bin/bash

set -e

export DOWN=${DOWN:-true}

docker-compose down

if [ "$DOWN" == false ]; then
  docker-compose up -d --scale worker=5
fi
