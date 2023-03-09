#! /bin/bash -x

set -e

cd ../postgresql/

. init.sh

cd ..

docker-compose up -d