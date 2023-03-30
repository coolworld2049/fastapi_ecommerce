#! /bin/bash

set -e

VOL_PATH=../src/.volumes

if [ ! -e "$VOL_PATH" ]; then
  mkdir ../src/.volumes
  chown -R 1001:1001 $VOL_PATH
  printf '\n%s\n' "✅ $VOL_PATH  "
else
  chown -R 1001:1001 $VOL_PATH
  printf '\n%s\n' "✅ $VOL_PATH already exist  "
fi

start=$SECONDS

ROOT_PATH=../src
CURDIR=../../scripts
DOCKER_OPTIONS=--no-build

source $ROOT_PATH/.env

#auth_service-----------------------------------------------------------------------------------------------------------
export SERVICE_PATH=$ROOT_PATH/auth_service

cd $SERVICE_PATH
docker-compose up -d "$DOCKER_OPTIONS" --scale auth_service=0
cd $CURDIR

cd $ROOT_PATH/postgresql
docker-compose up -d --scale slave="$POSTGRESQL_NUM_SLAVES"
echo "sleep 15"
sleep 15
cd $CURDIR

cd $ROOT_PATH/auth_service
docker-compose up -d "$DOCKER_OPTIONS"
cd $CURDIR

#store_service----------------------------------------------------------------------------------------------------------
export SERVICE_PATH=$ROOT_PATH/store_service

cd $SERVICE_PATH
docker-compose up -d "$DOCKER_OPTIONS" --scale store_service=0
cd $CURDIR

cd $ROOT_PATH/mongodb
docker-compose up -d
echo "sleep 5"
sleep 5
. init_cluster.sh
echo "sleep 10"
sleep 10
cd $CURDIR

cd $SERVICE_PATH
docker-compose up -d "$DOCKER_OPTIONS"
cd $CURDIR

#proxy------------------------------------------------------------------------------------------------------------------
export SERVICE_PATH=../src/proxy

cd $SERVICE_PATH
. ./mkcert.sh
docker-compose up -d "$DOCKER_OPTIONS"
cd $CURDIR

printf "\n%s\n\n" "✔️✔️✔️ started in $((SECONDS - start)) sec ✔️✔️✔️"

docker volume prune -f

docker network prune -f

printf '\n'

docker stats --no-stream

. test.sh
