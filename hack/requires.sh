#! /usr/bin/env bash

set -eou pipefail

log() { printf '\n%s\n' "$1" >&2; }

for dir in ../src/*; do
  req="$dir/$(basename "$dir")/requirements.txt"
  if [[ -f $req ]]; then
    pip install -U -r "$req"
    log "✅ $req - Successfully installed"
  fi
done
