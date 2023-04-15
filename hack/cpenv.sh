#! /usr/bin/env bash

set -euo pipefail

log() { printf '\n%s' "$1" >&2; }
log_t() { printf '\n\t%s' "$1" >&2; }

function cpenv() {
  log "$(basename "$dir")"
  target_f_name="$dir"/.env
  example_f_name="$target_f_name".example
  if [ -f "$example_f_name" ]; then
    cp "$example_f_name" "$target_f_name"
    log_t "✅  file created $(basename "$target_f_name")"
  else
    log_t "$(basename "$example_f_name") FileNotFound"
  fi
}

for dir in ../databases/*; do
  cpenv "$dir"
done

for dir in ../src/*; do
  cpenv "$dir"
done
