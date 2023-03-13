#! /bin/bash -x

set -e

prisma generate --schema /prisma/schema.prisma

prisma db push --schema /prisma/schema.prisma

prisma studio --port "${PRISMA_STUDIO_PORT}" --browser none