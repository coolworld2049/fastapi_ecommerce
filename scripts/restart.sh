#! /bin/bash

set -e

RMI=true
RMV=false
RUN_BUILD_PUSH=true


. down.sh
. down.sh

if [ $RUN_BUILD_PUSH == true ]; then
  echo "exec build_push.sh ..."
  . build_push.sh
fi

. start.sh