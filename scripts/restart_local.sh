#! /bin/bash

set -e

start=$SECONDS

export RMI=true

. down.sh

export DOCKER_OPTIONS=--build

. start.sh

printf "\n"

echo "✔️✔️✔️ restarted in $((SECONDS - start)) sec ✔️✔️✔️"

printf "\n"
