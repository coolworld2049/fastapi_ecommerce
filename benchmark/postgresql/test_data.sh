#! /bin/bash -x

set -e

LOG_FLE="$APP_ENV"_"$(date '+%d-%m-%Y')"_"$(date +%s)".log

for f in /postgresql/*.sql; do
  printf '%s\n' "execute $f"
  until psql -U "$POSTGRESQL_USERNAME" -h "$POSTGRESQL_MASTER_HOST" -p "$POSTGRESQL_MASTER_PORT" -d "$POSTGRESQL_DATABASE" \
    -f "$f"; do
    echo "Try again"
  done
done >>"$LOG_FLE"
