#! /bin/bash

set -e

start=$SECONDS

. down.sh

. start.sh

printf "\n"

echo "✅ " restarted in $((SECONDS - start)) sec
