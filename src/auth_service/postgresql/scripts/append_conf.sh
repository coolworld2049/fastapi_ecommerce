#! /usr/bin/env bash

set -e

if [ "$APP_ENV" != dev ]; then
  part=."$APP_ENV"
else
  part=''
fi

new=/bitnami/postgresql/custom_conf/postgresql"$part".conf
old=/opt/bitnami/postgresql/conf/postgresql.conf
saved_old=/bitnami/postgresql/custom_conf/postgresql.conf.saved

function mod_pg_conf() {
  cat $saved_old $new >$old
}

if [ -f $saved_old ]; then
  mod_pg_conf
else
  cat $old >$saved_old
  mod_pg_conf
fi

if [ $? -eq 0 ]; then
  echo "✅  postgresql.conf changed successfully"
else
  echo "❌  error changing postgresql.conf"
fi
