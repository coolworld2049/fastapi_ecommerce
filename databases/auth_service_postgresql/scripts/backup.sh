#! /usr/bin/env bash

set -eou pipefail

log() { printf '\n%s\n' "$1"; }

function print_last_command_result() {
  if [ $? -eq 0 ]; then
    log "✅  $1"
  else
    log "❌  $1"
    exit 1
  fi
}

function backup() {
  log "PG_DUMP"
  pg_dump -U "$POSTGRESQL_USERNAME" -Ft "$POSTGRESQL_DATABASE" >"$backup_path"/"$file_name"
  print_last_command_result "$backup_path"/"$file_name"
  log "PG_DUMPALL"
  pg_dumpall -U "$POSTGRESQL_USERNAME" -g | gzip >"$backup_path"/globals."$file_name"
  print_last_command_result "$backup_path"/globals."$file_name"

}

function restore_globals() {
  gunzip <"$latest_backup_path"/globals."$file_name" |
    psql -U "$POSTGRESQL_USERNAME" \
      -tc "SELECT 1 FROM pg_database WHERE datname = '$POSTGRESQL_DATABASE'" | grep -q 1 ||
    psql -U "$POSTGRESQL_USERNAME" \
      -c "CREATE DATABASE  $POSTGRESQL_DATABASE"
  print_last_command_result "$latest_backup_path"/globals."$file_name"

}

function restore_db() {
  pg_restore -U "$POSTGRESQL_USERNAME" --clean --if-exists -Ft -d "$POSTGRESQL_DATABASE" <"$latest_backup_path"/"$file_name"
  print_last_command_result "$latest_backup_path"/"$file_name"

}

function main() {
  export PGPASSWORD=${POSTGRESQL_USERNAME? env required}
  dir=/mnt/server/archive/backup
  file_name="$POSTGRESQL_DATABASE".tar.gz
  if [ "$1" == 'backup' ]; then
    backup_path="$dir"/"$(date +%d-%m-%Y-%I-%M-%S-%p)"
    [ -d "$backup_path" ] || mkdir "$backup_path"
    backup
  elif [ "$1" == 'restore' ]; then
    latest_backup_path=$(find "$dir"/* | head -1)
    restore_globals
    restore_db
  elif [ -n "$1" ] || [ "$1" == '--help' ]; then
    printf '%s\n' "select [backup, restore]"
  fi
}

main "$1"
