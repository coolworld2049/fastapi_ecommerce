#! /bin/bash -x

set -e
export APP_ENV=${APP_ENV?env APP_ENV required e.g dev test prod}
if [ "$APP_ENV" == prod ]; then
  export APP_ENV=""
fi
cat /bitnami/postgresql/custom_conf/"$APP_ENV"/postgresql.conf >>/opt/bitnami/postgresql/conf/postgresql.conf
