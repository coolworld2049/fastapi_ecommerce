#! /bin/bash

set -e

cd ..

export RMI=true

. down.sh

cd dev

. start.dev.sh
