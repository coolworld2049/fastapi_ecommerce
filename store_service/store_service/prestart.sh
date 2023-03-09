#! /bin/bash -x

set -e

python ./store_service/pre_start.py

python -m prisma_cleanup

prisma generate

prisma db push