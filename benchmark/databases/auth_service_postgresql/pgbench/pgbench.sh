#! /usr/bin/env bash

set -e

WRITE_TX_MULTIPLIER=${WRITE_TX_MULTIPLIER:-1}
WRITE_CLIENT_MULTIPLIER=${WRITE_CLIENT_MULTIPLIER:-1}

READ_TX_MULTIPLIER=${READ_TX_MULTIPLIER:-1}
READ_CLIENT_MULTIPLIER=${READ_CLIENT_MULTIPLIER:-1}

proc_num=$(grep ^cpu\\scores /proc/cpuinfo | uniq | awk '{print $4}')
threads="$proc_num"

log() { printf '\n%s\n' "$1" >&2; }

LOG_DIR=./.logs
[ -d "$LOG_DIR" ] || mkdir "$LOG_DIR"

dt=$(date '+%d-%m-%Y')
ts=$(date +%s)

LOG_PATH="$LOG_DIR"/"$dt"_"$ts".txt

env >>"$LOG_PATH"

function until_success() {
  local_counter=0
  until [ $? -eq 0 ] || [ "$local_counter" -le 6 ]; do
    log "Try again. Attempt $local_counter"
    : $((local_counter++))
  done
}

pgbench -i -s "${SCALE:-50}" -U "$POSTGRESQL_USERNAME" \
  -h "$POSTGRESQL_MASTER_HOST" -p "$POSTGRESQL_MASTER_PORT" "$POSTGRESQL_DATABASE"
until_success

function pgbench_WRITE() {
  set +e
  pgbench -j "$threads" -c "$clients" -t "$transactions" \
    -U "$POSTGRESQL_USERNAME" -h "$POSTGRESQL_MASTER_HOST" \
    -p "$POSTGRESQL_MASTER_PORT" "$POSTGRESQL_DATABASE"
}

function pgbench_READ() {
  set +e
  psql -U "$POSTGRESQL_USERNAME" -h "$POSTGRESQL_MASTER_HOST" \
    -p "$POSTGRESQL_MASTER_PORT" -d "$POSTGRESQL_DATABASE" \
    -c "vacuum pgbench_branches" \
    -c "vacuum pgbench_tellers" \
    -c "truncate pgbench_history"
  until_success
  pgbench -j "$threads" -c "$clients" -t "$transactions" \
    -b select-only -U "$POSTGRESQL_USERNAME" -h "$POSTGRESQL_REPLICA_HOST" \
    -p "$POSTGRESQL_REPLICA_PORT" "$POSTGRESQL_DATABASE"
}

function log_options() {
  msg="$counter, $action, $clients, $transactions, $threads "
  log "$msg"
  printf "\n%s\n" "$msg" >>"$LOG_PATH"
}

counter=1
for i in $(seq 1000 500 4000); do
  for action in WRITE READ; do
    clients=$(((i / 10) * $"${action}_CLIENT_MULTIPLIER"))
    transactions=$((i * $"${action}_TX_MULTIPLIER"))
    log_options
    pgbench_$action
  done >>"$LOG_PATH"
  until_success
  : $((counter++))
done
