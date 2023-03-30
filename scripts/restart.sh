#! /bin/bash

set -e

. down.sh
. down.sh

export IS_BUILD_PUSH="${IS_BUILD_PUSH:-true}"

if [ "$APP_ENV" == true ]; then
  echo "exec build_push.sh ..."
  . build_push.sh
fi

export INIT_MONGODB_CLUSTER="${INIT_MONGODB_CLUSTER:-false}"

. start.sh
