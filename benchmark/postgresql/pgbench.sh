#! /bin/bash -x

set -e

# pgbench
#-I initialize the db. Creates a bunch of default tables
#-s  scaling option. i.e take the default rows and x 50 or whatever scaling number you require
#-c number of clients
#-j 2 number of threads
#-t amount of transactions

REQUIRED_PKG="postgresql-contrib"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG | grep "install ok installed")
echo Checking for $REQUIRED_PKG: "$PKG_OK"
if [ "" = "$PKG_OK" ]; then
  echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
  sudo apt-get --yes install $REQUIRED_PKG
fi
printf '\n'

export SCALE=${SCALE:-50}

pgbench -i -s "$SCALE" -U postgres -h "$POSTGRESQL_HOST" -p "$POSTGRESQL_PORT" "$POSTGRESQL_DATABASE"

printf '\n'

counter=1
for tx in 100 200 300 400 500; do
  set +e
  clients=$((tx / 10))
  transactions=$tx
  printf '%s\n'"test [$counter] options: clients=$clients transactions=$transactions "
  printf '\n'
  pgbench -j 2 -c $clients -t $transactions -U postgres -h "$POSTGRESQL_HOST" -p "$POSTGRESQL_PORT" "$POSTGRESQL_DATABASE"
  : $((counter++))
done
