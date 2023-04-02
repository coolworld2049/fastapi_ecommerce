#! /bin/bash

set -e

start=$SECONDS

export \
  DOCKER_UP_OPTIONS="${DOCKER_UP_OPTIONS:---build}" \
  SRC_PATH=../src \
  CURDIR=../../scripts \
  VOL_PATH=..src/.volumes

source $SRC_PATH/.env

printf '\n%s\n\n' "❗ APP_ENV=$APP_ENV"

if [ "$APP_ENV" == prod ]; then
  export DOCKER_UP_OPTIONS=--no-build
fi

if [ ! -e "$VOL_PATH" ]; then
  set +e
  mkdir ../src/.volumes
  chmod -R 777 $VOL_PATH/*
  printf '\n%s\n' "✅ $VOL_PATH created  "
else
  set +e
  chmod -R 777 $VOL_PATH/*
  printf '\n%s\n' "✅ $VOL_PATH already exist  "
fi

#auth_service-----------------------------------------------------------------------------------------------------------
printf '\n%s\n' "AUTH_SERVICE"
cd $SRC_PATH/auth_service
docker-compose up -d "$DOCKER_UP_OPTIONS" --scale auth_service=0
cd $CURDIR

cd $SRC_PATH/postgresql
if [ "$APP_ENV" == prod ]; then
  docker-compose up -d
else
  printf '\n%s\n' "❗ postgresql docker-compose.$APP_ENV.yml"
  docker-compose -f docker-compose."$APP_ENV".yml up -d
fi
printf '\n%s\n' "sleep 20"
sleep 20
cd $CURDIR

cd $SRC_PATH/auth_service
if [ "$APP_ENV" != dev ]; then
  docker-compose up -d "$DOCKER_UP_OPTIONS"
fi
cd $CURDIR
printf '\n%s\n' "✔️AUTH_SERVICE✔️"

#store_service----------------------------------------------------------------------------------------------------------
printf '\n%s\n' "STORE_SERVICE"
cd $SRC_PATH/store_service
docker-compose up -d "$DOCKER_UP_OPTIONS" --scale store_service=0
cd $CURDIR

cd $SRC_PATH/mongodb
docker-compose up -d

printf '\n%s\n' "sleep 5"
sleep 5
. init_cluster.sh
printf '\n%s\n' "sleep 10"
sleep 10
cd $CURDIR

cd $SRC_PATH/store_service
if [ "$APP_ENV" != dev ]; then
  docker-compose up -d "$DOCKER_UP_OPTIONS"
fi
cd $CURDIR
printf '\n%s\n' "✔️STORE_SERVICE✔️"

#proxy------------------------------------------------------------------------------------------------------------------
printf '\n%s\n' "PROXY"
cd $SRC_PATH/proxy
. ./mkcert.sh
docker-compose up -d "$DOCKER_UP_OPTIONS"
cd $CURDIR
printf '\n%s\n' "✔️PROXY✔️"

docker volume prune -f --filter "label!=keep"

docker network prune -f

printf '\n%s\n' "$(docker ps)"

printf '\n%s\n' "$(docker stats --no-stream)"

. test.sh

printf "\n%s\n\n" "✔️✔️✔️ started in $((SECONDS - start)) sec ✔️✔️✔️"
