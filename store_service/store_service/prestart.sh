#! /bin/bash -x

set -e

python ./store_service/pre_start.py

python -m prisma_cleanup

prisma generate

prisma db push

pytest /app/store_service/test -vv --tb=no -l --cov /app/store_service --cov-report=html
