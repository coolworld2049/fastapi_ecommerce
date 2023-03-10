#! /bin/bash -x

set -e

cd ..

# shellcheck disable=SC2046
# shellcheck disable=SC2002
export $(cat .env | xargs)

source .env

docker-compose -f docker-compose.pgcluster.yml up --detach --scale postgresql_master=1 --scale postgresql_slave=3

set +e

# shellcheck disable=SC2086
docker-compose exec -it postgresql_master psql -U ${POSTGRES_USER} -W ${POSTGRES_DB} -c "create database grafana;"

set -e

docker-compose up -d

docker-compose -f docker-compose.tools.yml up -d

