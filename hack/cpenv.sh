#! /bin/bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

for dir in ../src/*; do
  env_f=.env."$(basename "$dir")"
  env_f_example="$env_f".example
  if [ ! -f ../src/"$env_f_example" ]; then
    log "❌ ../src/$env_f_example File not exist"
  else
    cp ../src/"$env_f_example" ../src/"$env_f"
    log "✅ ../src/$env_f"
  fi
done
