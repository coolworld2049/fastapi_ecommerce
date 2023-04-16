#! /usr/bin/env bash

set -e

STAGE=${STAGE:-dev}

echo "env STAGE=$STAGE"

if [ "$STAGE" == prod ]; then
  part=""
else
  part=."$STAGE"
fi

file_name=postgresql"$part".conf
conf_path=/bitnami/postgresql/conf/$POSTGRESQL_REPLICATION_MODE
new=$conf_path/$file_name
old=/opt/bitnami/postgresql/conf/postgresql.conf
saved_old=$conf_path/postgresql.conf.saved

function mod_pg_conf() {
  cat "$saved_old" "$new" >$old
}

if [ -f "$saved_old" ]; then
  mod_pg_conf
else
  cat $old >"$saved_old"
  mod_pg_conf
fi

echo "$new extends $old"

if [ $? -eq 0 ]; then
  echo "✅  $file_name >> postgresql.conf"
else
  echo "❌  $file_name >> postgresql.conf"
fi
