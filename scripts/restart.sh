#! /bin/bash

set -e

. down.sh
. down.sh

if [ "$APP_ENV" != dev ]; then
  echo "exec build_push.sh ..."
  . build_push.sh
fi

export INIT_MONGODB_CLUSTER="${INIT_MONGODB_CLUSTER:-false}"

. start.sh
