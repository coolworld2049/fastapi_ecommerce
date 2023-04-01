#! /bin/bash -x

set -e

dt=$(date '+%d-%m-%Y')
ts=$(date +%s)
LOG_FLE="$APP_ENV"_"$dt"_"$ts".txt

printf '%s\n' "logs in $LOG_FLE"

REQUIRED_PKG="postgresql-contrib"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG | grep "install ok installed")
echo Checking for $REQUIRED_PKG: "$PKG_OK"
if [ "" = "$PKG_OK" ]; then
  echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
  sudo apt-get --yes install $REQUIRED_PKG
fi
printf '\n'

pgbench -i -s "${SCALE:-50}" -U "$POSTGRESQL_USERNAME" -h "$POSTGRESQL_MASTER_HOST" -p "$POSTGRESQL_MASTER_PORT" "$POSTGRESQL_DATABASE"

printf '\n'

counter=1
for i in $(seq 500 500 2000); do
  set +e
  proc_num="$(grep ^cpu\\scores /proc/cpuinfo | uniq | awk '{print $4}')"
  clients=$((i / 10))
  transactions=$i
  # WRITE
  printf '%s\n'"$counter, WRITE master, options clients=$clients transactions=$transactions threads=$proc_num "
  printf '\n'
  until pgbench -j "$proc_num" -c $clients -t "$transactions" \
    -U "$POSTGRESQL_USERNAME" -h "$POSTGRESQL_MASTER_HOST" -p "$POSTGRESQL_MASTER_PORT" "$POSTGRESQL_DATABASE"; do
    echo "Try again"
  done
  clients=$(((i / 10) * "$POSTGRESQL_NUM_SLAVES"))
  transactions=$((i * "$POSTGRESQL_NUM_SLAVES"))
  # READ
  printf '%s\n'"$counter, READ master [$counter], options clients=$clients transactions=$transactions threads=$proc_num "
  printf '\n'
  until pgbench -j "$proc_num" -c $clients -t "$transactions" \
    -b select-only -U "$POSTGRESQL_USERNAME" -h "$POSTGRESQL_SLAVE_HOST" -p "$POSTGRESQL_SLAVE_PORT" "$POSTGRESQL_DATABASE"; do
    echo "Try again"
  done
  : $((counter++))
done >>"$LOG_FLE"

cat "$LOG_FLE"
