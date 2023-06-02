#! /usr/bin/env bash

set -euo pipefail

log() { printf '\n%s' "$1" >&2; }

function convert() {
  target_f_name="$1"/$2
  example_f_name="$target_f_name".example
  if [ -f "$example_f_name" ]; then
    cp "$example_f_name" "$target_f_name"
    log "✅  $example_f_name > $target_f_name"
  fi
}

function main() {

  for dir in ../databases/*; do
    convert "$dir" .env
  done

  for dir in ../src/*; do
    convert "$dir" .env
  done
}

main