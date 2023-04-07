#! /usr/bin/env bash

set -e

prisma generate --schema /prisma/schema.prisma

prisma db push --schema /prisma/schema.prisma

prisma studio --port "${PRISMA_STUDIO_PORT:-5555}" --browser none