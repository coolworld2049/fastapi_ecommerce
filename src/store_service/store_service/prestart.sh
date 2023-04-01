#! /bin/bash

set -e

python ./store_service/pre_start.py

prisma generate

prisma db push

prisma --version

pytest ./store_service/test -v --tb=native --cov ./store_service --cov-report=html
