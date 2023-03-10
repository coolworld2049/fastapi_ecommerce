#! /bin/bash -x

set -e

cd ../mongodb/

. init.sh

cd ..

sleep 3

docker-compose -f docker-compose.yml up --detach --scale store_service=3

docker-compose -f docker-compose.tools.yml up -d

