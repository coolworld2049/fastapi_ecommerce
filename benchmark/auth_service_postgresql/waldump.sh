#! /usr/bin/env bash

set -e

# waldump

docker exec -i postgresql-master-1 bash <<'EOF'
#! /usr/bin/env bash

set -e

pg_wal_path=/bitnami/postgresql/data/pg_wal
oldest_file=$(find $pg_wal_path -type f | tail -n 1)
newest_file=$(find $pg_wal_path -type f | head -n 1)

output_filename='waldump'_"$(date '+%d-%m-%Y')"_"$(date +%s)".dat

pg_waldump -p /bitnami/postgresql/data/pg_wal \
  "$pg_wal_path/$newest_file" "$pg_wal_path/$oldest_file" > /bitnami/postgresql/"$output_filename"
exit
EOF
exit
