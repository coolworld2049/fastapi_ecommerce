#! /usr/bin/env bash

set -euo pipefail

restart=$SECONDS

. down.sh

. make_docker_images.sh

. start.sh

log "✔️✔️✔️ Successfully restarted in $((SECONDS - restart)) sec ✔️✔️✔️ "
