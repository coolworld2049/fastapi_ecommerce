#!/bin/bash

# Set the PostgreSQL connection parameters
PGHOST="auth-svc-pg-postgresql-primary.fastapi-ecommerce.svc.cluster.local"
PGPORT="5432"
PGUSER="postgres"
PGDATABASE="app"
POSTGRES_PASSWORD="postgres"

# Set the number of threads and duration for the test
THREADS=10
DURATION=60  # in seconds

# Create the pgbench tables
PGPASSWORD="$POSTGRES_PASSWORD" pgbench -i -s 100 -h $PGHOST -p $PGPORT -U $PGUSER $PGDATABASE

# Run the pgbench test
PGPASSWORD="$POSTGRES_PASSWORD" pgbench -c $THREADS -T $DURATION -h $PGHOST -p $PGPORT -U $PGUSER $PGDATABASE

# Generate a report
PGPASSWORD="$POSTGRES_PASSWORD" pgbench -i -s 100 -h $PGHOST -p $PGPORT -U $PGUSER $PGDATABASE
