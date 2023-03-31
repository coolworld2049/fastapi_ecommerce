#! /bin/bash

set -e

start=$SECONDS

export \
  DOCKER_OPTIONS="${DOCKER_OPTIONS:---build}" \
  ROOT_PATH=../src \
  CURDIR=../../scripts \
  VOL_PATH=../src/.volumes

source $ROOT_PATH/.env

printf '\n%s\n\n' "❗ APP_ENV=$APP_ENV"

if [ "$APP_ENV" == prod ]; then
  export DOCKER_OPTIONS=--no-build
fi

if [ ! -e "$VOL_PATH" ]; then
  set +e
  mkdir ../src/.volumes
  chmod -R 777 $VOL_PATH/*
  printf '\n%s\n' "✅ $VOL_PATH  "
else
  set +e
  chmod -R 777 $VOL_PATH/*
  printf '\n%s\n' "✅ $VOL_PATH already exist  "
fi

#auth_service-----------------------------------------------------------------------------------------------------------
export SERVICE_PATH=$ROOT_PATH/auth_service

cd $SERVICE_PATH
docker-compose up -d "$DOCKER_OPTIONS" --scale auth_service=0
cd $CURDIR

if [ "$APP_ENV" != dev ]; then
  cd $ROOT_PATH/postgresql
  docker-compose up -d --scale slave="$POSTGRESQL_NUM_SLAVES"
  echo "sleep 20"
  sleep 20
  cd $CURDIR
else
  cd $ROOT_PATH/postgresql
  docker-compose -f docker-compose.dev.yml up -d
  cd $CURDIR
fi

if [ "$APP_ENV" != dev ]; then
  cd $ROOT_PATH/auth_service
  docker-compose up -d "$DOCKER_OPTIONS"
  cd $CURDIR
fi

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

if [ "$APP_ENV" != dev ]; then
  cd $SERVICE_PATH
  docker-compose up -d "$DOCKER_OPTIONS"
  cd $CURDIR
fi

#proxy------------------------------------------------------------------------------------------------------------------
export SERVICE_PATH=../src/proxy

if [ "$APP_ENV" != dev ]; then
  cd $SERVICE_PATH
  . ./mkcert.sh
  docker-compose up -d "$DOCKER_OPTIONS"
  cd $CURDIR
fi

printf "\n%s\n\n" "✔️✔️✔️ started in $((SECONDS - start)) sec ✔️✔️✔️"

docker volume prune -f

docker network prune -f

printf '\n'

docker ps

printf '\n'

docker stats --no-stream

. test.sh
