#! /bin/bash

set -e

psql -U postgres -c "create table if not exists benchmark (scale int not null, table_size_mb int not null, index_size_mb int not null, db_size_mb int not null);"

for x in $(seq 50 50 450); do
  pgbench -i --unlogged-tables -s "$x" -n &>/tmp/pgbench.log
  SQL=$(
    cat <<-EOF

  insert into benchmark select

  ${x},

  (select round(pg_table_size('pgbench_accounts') / 1024^2)),

  (select round(pg_relation_size('pgbench_accounts_pkey') / 1024^2)),

  (select round(pg_database_size(current_database()) / 1024^2))

EOF
  )
  echo "$SQL" | psql
done
