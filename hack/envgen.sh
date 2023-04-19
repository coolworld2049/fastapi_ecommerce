#! /usr/bin/env bash

set -euo pipefail

log() { printf '\n%s' "$1" >&2; }
log_t() { printf '\n\t%s' "$1" >&2; }

save_f_name=../.generated/samples

[ -d $save_f_name ] || mkdir -p $save_f_name

function cpenv() {
  log "$(basename "$dir")"
  target_f_name="$dir"/.env
  example_f_name="$target_f_name".example
  f_name="$save_f_name/$(basename "$dir").env"
  if [ -f "$example_f_name" ]; then
    cp "$example_f_name" "$f_name"
    log_t "✅  file created $f_name"
  else
    log_t "$(basename "$example_f_name") FileNotFound"
  fi
}

for dir in ../src/*; do
  cpenv "$dir"
done

dir=../../fastapi-ecommerce
cpenv "$dir"