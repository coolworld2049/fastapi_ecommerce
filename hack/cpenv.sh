#! /bin/bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

for dir in ../src/*; do
  env_f=.env."$(basename "$dir")"
  env_f_example="$env_f".example
  if [ -f ../src/"$env_f_example" ]; then
    #cp ../src/"$env_f_example" ../src/"$env_f"
    log "✅  created ../src/$env_f"
  else
    log "❌ ../src/$env_f_example File not exist"
  fi

  if [ -f "$dir"/.env.example ]; then
    #cp "$dir"/.env.example "$dir"/.env
    log "✅  created $dir/.env"
  else
    log "❌ $dir/.env.example File not exist"
  fi
done
