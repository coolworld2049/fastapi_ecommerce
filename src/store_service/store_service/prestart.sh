#! /usr/bin/env bash

set -e

# python ./store_service/pre_start.py

python -m prisma_cleanup

prisma generate

prisma --version

prisma db push

pytest ./store_service/test -v --tb=native --cov ./store_service --cov-report=html
