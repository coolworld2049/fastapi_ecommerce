#! /usr/bin/env bash

set -e

python -m prisma_cleanup

prisma generate

prisma db push