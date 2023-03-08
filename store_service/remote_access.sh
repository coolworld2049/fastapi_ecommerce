#! /bin/bash -x

# shellcheck disable=SC2046
# shellcheck disable=SC2002
export $(cat .env | xargs)

sudo ufw allow from "$REMOTE_DB_IP"
