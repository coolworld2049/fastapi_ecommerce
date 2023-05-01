#! /usr/bin/env bash

set -euo pipefail

function gen_sample_enf_files() {
  log() { printf '\n%s' "$1" >&2; }
  log_t() { printf '\n\t%s' "$1" >&2; }

  save_f_name=../.generated/samples

  set +e
  rm -R $save_f_name
  set -e

  mkdir -p $save_f_name

  function cpenv() {
    log "$(basename "$dir")"
    target_f_name="$dir"/.env.prod
    example_f_name="$target_f_name".example
    f_name="$save_f_name/$(basename "$dir").env.prod"
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

  cp ../.env.example "$save_f_name"/fastapi-ecommerce.env
}

gen_sample_enf_files