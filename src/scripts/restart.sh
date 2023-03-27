#! /bin/bash

set -e

start=$SECONDS

. down.sh

. build_push.sh

. start.sh

printf "\n"

echo "✅ " restarted in $((SECONDS - start)) sec
