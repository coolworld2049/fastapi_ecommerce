#! /usr/bin/env bash

set -eou pipefail

function pgbench_init() {
  log ""
  pgbench -i -s "${SCALE:-50}" -U "$POSTGRESQL_USERNAME" \
    -h "$POSTGRESQL_MASTER_HOST" -p "$POSTGRESQL_MASTER_PORT" "$POSTGRESQL_DATABASE"
  log "✅ pgbench_init"
}

function pgbench_WRITE() {
  set +e
  pgbench -j "$threads" -c "$clients" -t "$transactions" \
    -U "$POSTGRESQL_USERNAME" -h "$POSTGRESQL_MASTER_HOST" \
    -p "$POSTGRESQL_MASTER_PORT" "$POSTGRESQL_DATABASE"
}

function pgbench_READ() {
  set +e
  log "vacuum and truncate pgbench tables before errors"
  psql -U "$POSTGRESQL_USERNAME" -h "$POSTGRESQL_MASTER_HOST" \
    -p "$POSTGRESQL_MASTER_PORT" -d "$POSTGRESQL_DATABASE" \
    -c "vacuum pgbench_branches" \
    -c "vacuum pgbench_tellers" \
    -c "truncate pgbench_history"
  pgbench -j "$threads" -c "$clients" -t "$transactions" \
    -b select-only -U "$POSTGRESQL_USERNAME" -h "$POSTGRESQL_REPLICA_HOST" \
    -p "$POSTGRESQL_REPLICA_PORT" "$POSTGRESQL_DATABASE"
}

function log_options() {
  msg="$counter,$action,$clients,$transactions,$threads "
  log "$msg"
  log_f "$msg"
}

function main() {
  log() { printf '\n%s\n' "$1" >&2; }

  LOG_DIR=./.logs/"$(date '+%d-%m-%Y')"_"$(date +%s)"

  [ -d "$LOG_DIR" ] || mkdir -p "$LOG_DIR"

  LOG_PATH="$LOG_DIR"/log.txt

  log_f() { printf '\n%s\n' "$1" >>"$LOG_PATH"; }

  export PGPASSWORD="$POSTGRESQL_PASSWORD"

  WRITE_TX_MULTIPLIER=${WRITE_TX_MULTIPLIER:-1}
  WRITE_CLIENT_MULTIPLIER=${WRITE_CLIENT_MULTIPLIER:-1}

  READ_TX_MULTIPLIER=${READ_TX_MULTIPLIER:-1}
  READ_CLIENT_MULTIPLIER=${READ_CLIENT_MULTIPLIER:-1}

  proc_num="$(grep ^cpu\\scores /proc/cpuinfo | uniq | awk '{print $4}')"
  threads="$proc_num"

  env >>"$LOG_PATH"

  for replica_type in master replica; do
    path="$LOG_DIR"/postgresql."$replica_type".txt
    printf '\n%s\n' "replica_type is $replica_type" >>"$path"
    log "export postgresql $replica_type conf to file"
    psql -U "$POSTGRESQL_USERNAME" -h "$POSTGRESQL_MASTER_HOST" \
      -p "$POSTGRESQL_MASTER_PORT" -d "$POSTGRESQL_DATABASE" \
      -c "show all" >>"$path"
  done

  log_f "Results"
  log_f 'Counter,Action,Clients,Transactions,Threads'

  pgbench_init

  counter=1
  for i in $(seq 1000 1000 6000); do
    for action in WRITE READ; do
      clients=$(((i / 10) * $"${action}_CLIENT_MULTIPLIER"))
      transactions=$((i * $"${action}_TX_MULTIPLIER"))
      log_options
      pgbench_$action
    done >>"$LOG_PATH"
    : $((counter++))
  done
}

main
