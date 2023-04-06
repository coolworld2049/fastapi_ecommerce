#! /bin/bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

for dir in ../src/*; do
  if [ -f "$dir"/.env.example ]; then
    cp "$dir"/.env.example "$dir"/.env
    log "✅  created $dir/.env"
  else
    log "❌ $dir/.env.example File not exist"
  fi
done
