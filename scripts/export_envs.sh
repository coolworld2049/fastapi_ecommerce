#! /bin/bash

set +e

ROOT_PATH=../src

function get_service_envs() {
  sp=$SERVICE_PATH/.env
  declare message
  if [ -f "$sp" ]; then
    # shellcheck disable=SC2046
    export $(grep -v '^#' "$sp" | xargs)
    message+="✅ $sp; "
  elif [ "$SERVICE_PATH" == "" ]; then
    message+="❌ SERVICE_PATH=$SERVICE_PATH; "
  else
    message+="❌ $sp; "
  fi
  rp=$ROOT_PATH/.env
  # shellcheck disable=SC2181
  if [ -f "$rp" ]; then
    # shellcheck disable=SC2046
    export $(grep -v '^#' $rp | xargs)
    message+="✅ $rp; "
  else
    message+="❌ $rp; "
  fi
  echo "$message"
}

get_service_envs "$SERVICE_PATH"
