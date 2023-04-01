#! /bin/bash -x

set -e

REQUIRED_PKG="postgresql-contrib"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG | grep "install ok installed")
echo Checking for $REQUIRED_PKG: "$PKG_OK"
if [ "" = "$PKG_OK" ]; then
  echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
  sudo apt-get --yes install $REQUIRED_PKG
fi
printf '\n'

pgbench -i -s "${SCALE:-50}" -U "$POSTGRESQL_USERNAME" -h "$POSTGRESQL_MASTER_HOST" \
  -p "$POSTGRESQL_MASTER_PORT" "$POSTGRESQL_DATABASE"

printf '\n'

proc_num="$(grep ^cpu\\scores /proc/cpuinfo | uniq | awk '{print $4}')"
until pgbench -j "$proc_num" -R 100 -T 120 \
  -U "$POSTGRESQL_USERNAME" -h "$POSTGRESQL_MASTER_HOST" -p "$POSTGRESQL_MASTER_PORT" "$POSTGRESQL_DATABASE"; do
  echo 'Try again'
done
