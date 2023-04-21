#! /usr/bin/env bash

set -e

STAGE=${STAGE:-dev}

if [ "$STAGE" == prod ]; then
  part=""
else
  part=.dev
fi

conf_path=/bitnami/postgresql/conf
conf_path_pg_hba_f=$conf_path/pg_hba.conf
conf_path_repl_mode=/bitnami/postgresql/custom_conf/$POSTGRESQL_REPLICATION_MODE
conf_path_repl_mode_pg_hba=$conf_path_repl_mode/pg_hba"$part".conf

[ -d $conf_path ] || mkdir $conf_path

if [ -f "$conf_path_repl_mode_pg_hba" ]; then
  cat "$conf_path_repl_mode_pg_hba" >conf_path_pg_hba_f
  echo "✅  $conf_path_repl_mode_pg_hba >> $conf_path_pg_hba_f"
  else
  echo "❌  $conf_path_repl_mode_pg_hba >> $conf_path_pg_hba_f"
fi
