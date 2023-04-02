#! /bin/bash

set -e

restart=$SECONDS

. down.sh
. down.sh

if [ "$APP_ENV" == prod ]; then
  echo "exec build_push.sh ..."
  . build_push.sh
fi

. start.sh

printf "\n%s\n\n" "✔️✔️✔️ restarted in $((SECONDS - restart)) sec ✔️✔️✔️"
