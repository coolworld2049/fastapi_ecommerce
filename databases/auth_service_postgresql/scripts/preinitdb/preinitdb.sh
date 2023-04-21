#! /usr/bin/env bash

set -e

STAGE=${STAGE:-dev}

if [ "$STAGE" == prod ]; then
  part=""
else
  part=.dev
fi

conf_path=/opt/bitnami/postgresql/conf
conf_path_repl_mode=/bitnami/postgresql/custom_conf/$POSTGRESQL_REPLICATION_MODE
postgresql_conf_f_old=$conf_path/postgresql.conf
postgresql_conf_f_new=$conf_path_repl_mode/postgresql"$part".conf
postgresql_conf_f_saved=$conf_path_repl_mode/postgresql.conf.saved

function mod_pg_conf() {
  cat "$postgresql_conf_f_saved" "$postgresql_conf_f_new" >$postgresql_conf_f_old
}

if [ -f "$postgresql_conf_f_new" ] && [ -f "$postgresql_conf_f_saved" ]; then
  mod_pg_conf
else
  cat $postgresql_conf_f_old >"$postgresql_conf_f_saved"
  mod_pg_conf
fi

if [ $? -eq 0 ]; then
  echo "✅  $postgresql_conf_f_new >> $postgresql_conf_f_old"
else
  echo "❌  $postgresql_conf_f_new >> $postgresql_conf_f_old"
fi
