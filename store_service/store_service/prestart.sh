#! /bin/bash -x

set -e

python ./store_service/pre_start.py

prisma --version

prisma generate

prisma db push

pytest /app/store_service/test -v  --cov /app/store_service --cov-report=html
