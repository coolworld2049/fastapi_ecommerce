#! /bin/bash

set -e

log() { printf '\n%s\n' "$1" >&2; }

for dir in ../src/*; do
  set +e && file="$dir"/.env.example
  if [ ! -e "$file" ]; then
    log "❌ $dir/.env.example File not exist"
  else
    cp "$dir"/.env.example "$dir"/.env
    log "✅ $dir/.env  "
  fi
done
