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

function check_file() {
  # $1 dir
  # $2 filename
  [[ -f "$1"/"$2" ]]
  print_last_command_result "[ -f $1/$2 ]"
}

function raise_exc_env_required() {
  if [ "$2" == "" ]; then
    log "❗ env var $1 required"
    exit 1
  fi
}

function save_orig_conf() {
  cat "$conf_f_orig" >"$conf_f_saved"
  print_last_command_result "$conf_f_orig >$conf_f_saved"
}

function copy_to_confd() {
  cp "$custom_conf_path"/*"$part".conf "$conf_path"/conf.d
  print_last_command_result "cp $custom_conf_path/*$part.conf $conf_path/conf.d"
}

function modify_postgresql_conf() {
  copy_to_confd
  cat "$conf_f_saved" "$conf_f_new" >"$conf_f_orig"
  print_last_command_result "$conf_f_saved $conf_f_new >$conf_f_orig"
}

function mount_archive_dir() {
  [ -d "$1" ] || mkdir 700 -p "$1"
  chown postgres "$1"
  print_last_command_result "$1"
}

function main() {

  log() { printf '\n%s\n' "$1" >&2; }

  ARCHIVE_DIR=${ARCHIVE_DIR-/mnt/server/archive}

  log "mount_archive_dir ..."
  mount_archive_dir "$ARCHIVE_DIR"

  STAGE=${STAGE-""}
  raise_exc_env_required 'STAGE' "$STAGE"

  if [ "$STAGE" == prod ] || [ "$STAGE" == test ]; then
    part=""
  else
    part=.dev
  fi
  print_last_command_result "STAGE=$STAGE (part of conf path)"

  conf_path=/opt/bitnami/postgresql/conf
  custom_conf_path=/bitnami/postgresql/custom_conf
  custom_conf_path_mode=$custom_conf_path/$POSTGRESQL_REPLICATION_MODE

  conf_f_orig=$conf_path/postgresql.conf
  conf_f_saved=$conf_path/postgresql.conf.saved
  conf_f_new=$custom_conf_path_mode/postgresql"$part".conf

  log "check_files ..."
  check_file "$custom_conf_path" common.conf
  check_file "$custom_conf_path_mode" postgresql.conf

  log "modify_postgresql_conf ..."
  if [ -f "$conf_f_new" ] && [ -f "$conf_f_saved" ]; then
    modify_postgresql_conf
  else
    save_orig_conf
    modify_postgresql_conf
  fi
}

main
