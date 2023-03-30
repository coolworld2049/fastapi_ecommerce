#! /bin/bash

set -e

ROOT_PATH=../src
SCRIPTS_PATH=../../scripts
DOCKER_OPTIONS=--no-build


# auth_service
export SERVICE_PATH=$ROOT_PATH/auth_service
. export_envs.sh
cd $SERVICE_PATH
docker-compose up -d "$DOCKER_OPTIONS" \
  --scale auth_service=0
cd $SCRIPTS_PATH

cd $ROOT_PATH/postgresql
docker-compose up -d \
  --scale slave="${POSTGRESQL_NUM_SLAVES}"
echo "sleep 10"
sleep 15
cd $SCRIPTS_PATH

cd $ROOT_PATH/auth_service
docker-compose up -d "$DOCKER_OPTIONS"
cd $SCRIPTS_PATH



# store_service
export SERVICE_PATH=$ROOT_PATH/store_service
. export_envs.sh

cd $SERVICE_PATH
docker-compose up -d "$DOCKER_OPTIONS" --scale store_service=0
cd $SCRIPTS_PATH

cd $ROOT_PATH/mongodb
docker-compose up -d
echo "sleep 5"
sleep 5
. init_cluster.sh
echo "sleep 10"
sleep 10
cd $SCRIPTS_PATH

cd $SERVICE_PATH
docker-compose up -d "$DOCKER_OPTIONS"
cd $SCRIPTS_PATH



# proxy
export SERVICE_PATH=../src/proxy
. export_envs.sh

cd $SERVICE_PATH
. ./mkcert.sh
docker-compose up -d "$DOCKER_OPTIONS"
cd $SCRIPTS_PATH

docker volume prune -f --filter "label!=keep"

. test.sh