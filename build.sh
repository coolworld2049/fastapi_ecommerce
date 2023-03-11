#! /bin/bash -x

set -e

cd auth_service/scripts

. ./build.sh

cd ../..

cd store_service/scripts

. ./build.sh

cd ../..
