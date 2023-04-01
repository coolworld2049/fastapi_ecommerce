#! /bin/bash

set -e

. down.sh
. down.sh

if [ "$APP_ENV" == 'prod' ]; then
  echo "exec build_push.sh ..."
  . build_push.sh
fi

. start.sh
