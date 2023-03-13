#! /bin/bash -x

set -e

cd auth_service/scripts

. ./build.sh

cd ..

sleep 3

cd store_service/scripts

. ./build.sh

