#! /usr/bin/env bash

source .env ../../.env

docker-compose down
docker-compose up -d
