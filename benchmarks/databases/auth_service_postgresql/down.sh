#! /usr/bin/env bash

set -e

docker rm -f auth_service_postgresql_bm

docker volume prune -f --filter "label!=keep"
