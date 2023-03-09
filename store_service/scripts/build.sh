#! /bin/bash -x

set -e

cd ../mongodb/

. init.sh

cd ..

docker-compose up -d