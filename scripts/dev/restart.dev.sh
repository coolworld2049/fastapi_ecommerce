#! /bin/bash

set -e

cd ..

export RMI=true RMV=true

. down.sh

cd dev

export DOCKER_OPTIONS=--build

. start.dev.sh
