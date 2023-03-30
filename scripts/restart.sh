#! /bin/bash

set -e

start=$SECONDS

export RMI=true

. down.sh

. build_push.sh

. start.sh

printf "\n"

echo "✔️✔️✔️ restarted in $((SECONDS - start)) sec ✔️✔️✔️"

printf "\n"
