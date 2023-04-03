#! /bin/bash

set -e

restart=$SECONDS

. down.sh

. start.sh

log "✔️✔️✔️ Successfully restarted in $((SECONDS - restart)) sec ✔️✔️✔️ "
