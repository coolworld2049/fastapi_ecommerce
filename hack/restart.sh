#! /usr/bin/env bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

restart=$SECONDS

. down.sh

. start.sh

log "✔️✔️✔️ Successfully restarted in $((SECONDS - restart)) sec ✔️✔️✔️ "
