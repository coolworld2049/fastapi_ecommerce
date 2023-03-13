#! /bin/bash -x

set -e

cd ..

docker-compose -f docker-compose.yml up -d --scale postgresql_master=1 --scale postgresql_slave=2


