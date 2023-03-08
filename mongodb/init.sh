#! /bin/bash -x

set -e

# shellcheck disable=SC2046
# shellcheck disable=SC2002
export $(cat .env | xargs)

docker-compose exec configsvr01 sh -c "mongosh < /scripts/init-configserver.js"
docker-compose exec shard01-a sh -c "mongosh < /scripts/init-shard01.js"
docker-compose exec shard02-a sh -c "mongosh < /scripts/init-shard02.js"

docker-compose exec router01 sh -c "mongosh < /scripts/init-router.js"

. enable_sharding.sh

. verify.sh

. info.sh
