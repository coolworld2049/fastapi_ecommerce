#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m'

# Set the default PostgresSQL connection parameters
DEFAULT_PGHOST="auth-postgresql-primary"
DEFAULT_PGPORT="5432"
PGUSER="postgres"
PGDATABASE="app"
POSTGRES_PASSWORD="postgres"

# Set the number of threads and duration for the test
THREADS="$(grep ^cpu\\scores /proc/cpuinfo | uniq | awk '{print $4}')"
THREADS="$(("$THREADS" / 2))"
SCALE=${SCALE:-50}
CLIENTS=${CLIENTS:-1000}
TX=${TX:-5000} # in seconds

# Function to display usage instructions
show_help() {
  echo "Usage: ./pgbench.sh [OPTIONS]"
  echo "Run pgbench test with configurable PostgresSQL connection parameters."
  echo
  echo "Options:"
  echo "  --host     PostgresSQL server hostname (default: $DEFAULT_PGHOST)"
  echo "  --port     PostgresSQL server port (default: $DEFAULT_PGPORT)"
  echo "  --tpcb     Run TPC_B test"
  echo "  --select   Run select_only test"
  echo "  --help     Show help information"
  echo "Examples:"
  echo "  bash pgbench.sh --host auth-postgresql-slave --port 5433 --select"
  echo "  bash pgbench.sh --host auth-postgresql-primary --port 5432 --tpcb"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
  --host)
    PGHOST="$2"
    shift # past argument
    shift # past value
    ;;
  --port)
    PGPORT="$2"
    shift # past argument
    shift # past value
    ;;
  --tpcb)
    TEST="TPC_B"
    shift # past argument
    ;;
  --select)
    TEST="select_only"
    shift # past argument
    ;;
  --help)
    show_help
    exit 0
    ;;
  *) # unknown option
    echo "ERROR: Unknown option: $key"
    exit 1
    ;;
  esac
done

# Set the PostgresSQL connection parameters
PGHOST="${PGHOST:-$DEFAULT_PGHOST}"
PGPORT="${PGPORT:-$DEFAULT_PGPORT}"

export PGPASSWORD="$POSTGRES_PASSWORD"

function init() {
  pgbench -i -s "$SCALE" -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" "$PGDATABASE"
}

function result_msg() {
  echo -e "${GREEN}test_type=$TEST, clients=$1, transactions=$2${NC}"
}

function TPC_B() {
  result_msg "$1" "$2"
  pgbench -j "$THREADS" -c "$1" -t "$2" -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" "$PGDATABASE"
}

function select_only() {
  result_msg "$1" "$2"
  pgbench -b select-only -j "$THREADS" -c "$1" -t "$2" -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" "$PGDATABASE"
}

init
for i in $(seq 100 100 "$CLIENTS"); do
  j="$(("$i" * 5))"
  # Run the selected test
  if [ "$TEST" == "TPC_B" ]; then
    TPC_B "$i" "$j"
  elif [ "$TEST" == "select_only" ]; then
    select_only "$(("$i" * 2))" "$(("$j" * 2))"
  else
    break
    show_help
  fi
  printf "\n"
done
