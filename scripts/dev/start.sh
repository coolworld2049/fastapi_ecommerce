#! /bin/bash

set -e

cd ..

ROOT_PATH=../src
SCRIPTS_PATH=../../scripts
DOCKER_OPTIONS=--build

# auth_service
export SERVICE_PATH=$ROOT_PATH/auth_service
source ../src/.env $SERVICE_PATH
cd $SERVICE_PATH
docker-compose up -d "$DOCKER_OPTIONS" --scale auth_service=0
cd $SCRIPTS_PATH

cd $ROOT_PATH/postgresql
docker-compose -f docker-compose.dev.yml up -d
cd $SCRIPTS_PATH

# store_service
export SERVICE_PATH=$ROOT_PATH/store_service
source ../src/.env $SERVICE_PATH

cd $SERVICE_PATH
docker-compose up -d "$DOCKER_OPTIONS" --scale store_service=0
cd $SCRIPTS_PATH

cd $ROOT_PATH/mongodb
docker-compose up -d
. init_cluster.sh
cd $SCRIPTS_PATH

echo "sleep 5"
sleep 5
cd $SERVICE_PATH
prisma generate
prisma db push
cd $SCRIPTS_PATH

docker volume prune -f --filter "label!=keep"

. test.sh
