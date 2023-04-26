#! /usr/bin/env bash

set -eou pipefail

log() { printf '\n%s\n' "$1" >&2; }

function print_last_command_result() {
  if [ $? -eq 0 ]; then
    log "✅  $1"
  else
    log "❌  $1"
    exit 12
  fi
}

function backup() {
  log "PG_DUMP"
  pg_dump -U "$POSTGRESQL_USERNAME" -v -Ft "$POSTGRESQL_DATABASE" >"$save_path"/"$file_name"
  log "PG_DUMPALL"
  pg_dumpall -U "$POSTGRESQL_USERNAME" -v -g | gzip >"$save_path"/globals."$file_name"
} >"$save_path"/backup.log

function restore() {
  gunzip <"$restore_path"/globals."$file_name" |
    psql -U "$POSTGRESQL_USERNAME" \
      -tc "SELECT 1 FROM pg_database WHERE datname = '$POSTGRESQL_DATABASE'" | grep -q 1 ||
    psql -U "$POSTGRESQL_USERNAME" \
      -c "CREATE DATABASE  $POSTGRESQL_DATABASE"
  print_last_command_result "$restore_path"/globals."$file_name"

  pg_restore -U "$POSTGRESQL_USERNAME" -v -Ft -d "$POSTGRESQL_DATABASE" <"$restore_path"/"$file_name"
  print_last_command_result "$restore_path"/"$file_name"

} >"$restore_path"/restore.log

function main() {
  export PGPASSWORD=${POSTGRESQL_USERNAME? env required}
  dir=/mnt/server/archive/backup
  dt="$(date +%d-%m-%Y-%I-%M-%S-%p)"
  save_path="$dir"/"$dt"
  file_name="$POSTGRESQL_DATABASE".tar.gz
  log "dir=$dir, file_name=$file_name"
  if [ "$1" == 'backup' ]; then
    [ -d "$save_path" ] || mkdir "$save_path"
    print_last_command_result "$save_path"
    backup
    log "$(cat "$save_path"/backup.log)"
  elif [ "$1" == 'restore' ]; then
    restore_path=$(find "$dir"/* | head -1)
    restore
    log "$(cat "$restore_path"/restore.log)"
  else
    printf '%s\n' "select [backup, restore]"
  fi
}

main "$1"
