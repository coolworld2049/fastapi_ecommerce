#! /bin/bash -x

if [ ! -f .env ]
then
  # shellcheck disable=SC2046
  # shellcheck disable=SC2002
  export $(cat .env | xargs)
fi

sudo ufw allow from "$REMOTE_DB_IP"
