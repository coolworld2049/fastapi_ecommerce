#! /bin/bash

set -e

python ./store_service/pre_start.py

prisma --version

prisma generate

prisma db push

# pytest ./store_service/test -v  --cov ./store_service --cov-report=html
