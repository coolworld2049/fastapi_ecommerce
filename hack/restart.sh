#! /bin/bash

set -euo pipefail

restart=$SECONDS

. down.sh

. start.sh

log "✔️✔️✔️ Successfully restarted in $((SECONDS - restart)) sec ✔️✔️✔️ "
