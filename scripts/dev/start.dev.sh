#! /bin/bash

set -e

cd ..

ROOT_PATH=../src
SCRIPTS_PATH=../../scripts
DOCKER_OPTIONS=--build


# auth_service
export SERVICE_PATH=$ROOT_PATH/auth_service
. export_envs.sh
cd $SERVICE_PATH
docker-compose up -d "$DOCKER_OPTIONS" --scale auth_service=0
cd $SCRIPTS_PATH

cd $ROOT_PATH/postgresql
docker-compose -f docker-compose.dev.yml up -d
cd $SCRIPTS_PATH

#cd $ROOT_PATH/auth_service
#docker-compose up -d "$DOCKER_OPTIONS"
#cd $SCRIPTS_PATH



# store_service
export SERVICE_PATH=$ROOT_PATH/store_service
. export_envs.sh

cd $SERVICE_PATH
docker-compose up -d  "$DOCKER_OPTIONS" --scale store_service=0
cd $SCRIPTS_PATH

cd $ROOT_PATH/mongodb
docker-compose up -d
. init_cluster.sh
cd $SCRIPTS_PATH

#cd $SERVICE_PATH
#docker-compose up -d "$DOCKER_OPTIONS"
#cd $SCRIPTS_PATH



## proxy
#export SERVICE_PATH=../src/proxy
#. export_envs.sh
#
#cd $SERVICE_PATH
#. ./mkcert.sh
#docker-compose up -d "$DOCKER_OPTIONS"

cd $SCRIPTS_PATH

docker volume prune -f --filter "label!=keep"

. test.sh