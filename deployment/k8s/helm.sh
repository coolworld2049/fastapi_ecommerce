#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"/k8s
PG_SERVICE_NAME=auth-postgresql
MONGO_SERVICE_NAME=store-mongo
NAMESPACE="fastapi-ecommerce"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

log() {
  local color=$1
  shift
  # shellcheck disable=SC2145
  echo -e "${color}$@${NC}"
}

process_files_in_folder() {
  local action="$1"
  local folder_path="$2"
  log "${YELLOW}${action} *.yaml files in folder $folder_path ...${NC}"

  local files=("$folder_path"/* "$folder_path"/.*)
  shopt -s nullglob
  for file in "${files[@]}"; do
    if [ -f "$file" ] && [[ "$file" = *.yaml ]] && [[ "$file" != *example* ]]; then
      if [[ "$file" = *values*.yaml ]]; then
        continue
      fi
      if [ "$action" = "apply" ]; then
        kubectl apply -f "$file" -n "${NAMESPACE}"
      elif [ "$action" = "delete" ]; then
        kubectl delete -f "$file" -n "${NAMESPACE}"
      fi
    fi
  done
}

install_auth_postgresql() {
  log "${GREEN}Deploy auth-postgresql..."
  kubectl apply -f "${SCRIPT_DIR}"/auth-postgresql/auth-postgresql-configmap.yaml -n "${NAMESPACE}"
  helm install "$PG_SERVICE_NAME" -f "${SCRIPT_DIR}/auth-postgresql/auth-postgresql-values.yaml" \
    oci://registry-1.docker.io/bitnamicharts/postgresql -n "${NAMESPACE}"
}

delete_auth_postgresql() {
  log "${GREEN}Delete auth-postgresql..."
  helm delete "$PG_SERVICE_NAME" -n "${NAMESPACE}"
  process_files_in_folder delete "${SCRIPT_DIR}"/auth-postgresql
}

install_store_mongo() {
  log "${GREEN}Deploy store-mongo..."
  helm install "$MONGO_SERVICE_NAME" -f "${SCRIPT_DIR}/store-mongo/store-mongo-values.yaml" \
    oci://registry-1.docker.io/bitnamicharts/mongodb -n "${NAMESPACE}"
}

delete_store_mongo() {
  log "${GREEN}Delete store-mongo..."
  helm delete "$MONGO_SERVICE_NAME" -n "${NAMESPACE}"
  process_files_in_folder delete "${SCRIPT_DIR}"/store-mongo
}

install_auth() {
  log "${GREEN}Deploy auth..."
  process_files_in_folder apply "${SCRIPT_DIR}"/auth
}

delete_auth() {
  log "${GREEN}Delete auth..."
  process_files_in_folder delete "${SCRIPT_DIR}"/auth
}

install_store() {
  log "${GREEN}Deploy store..."
  process_files_in_folder apply "${SCRIPT_DIR}"/store
}

delete_store() {
  log "${GREEN}Delete store..."
  process_files_in_folder delete "${SCRIPT_DIR}"/store
}

install() {
  helm repo add bitnami https://charts.bitnami.com/bitnami
  install_auth_postgresql
  install_auth

  install_store_mongo
  install_store
}

delete() {
  delete_auth_postgresql
  delete_auth

  delete_store_mongo
  delete_store
}

port_forward() {
  local service_name="$1"

  case "$service_name" in
  auth)
    kubectl port-forward --namespace "${NAMESPACE}" "svc/${service_name}" 8081:8081 &
    echo "Port forwarding enabled for service ${service_name}"
    ;;
  auth-postgresql)
    kubectl port-forward --namespace "${NAMESPACE}" "svc/${service_name}-primary" 5432:5432 &
    kubectl port-forward --namespace "${NAMESPACE}" "svc/${service_name}-slave" 5433:5433 &
    echo "Port forwarding enabled for service ${service_name} (primary and slave)"
    ;;
  store-mongo)
    kubectl port-forward --namespace "${NAMESPACE}" "svc/${service_name}-headless" 27017:27017 &
    echo "Port forwarding enabled for service ${service_name} (headless)"
    ;;
  *)
    log "${RED}Error: Unknown service name."
    show_help
    exit 1
    ;;
  esac
}

show_help() {
  echo "Usage: script.sh [install|upgrade|delete|help] [OPTIONS]"
  echo "  install                             Start the script"
  echo "  delete                              Stop the script"
  echo "  port_forward, -pf <service_name>    Enable port forwarding"
  echo "  help                                Show help"
  echo ""
  echo "Options:"
  echo "  -n, --namespace                     Namespace"
}

while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
  -n | --namespace)
    NAMESPACE="$2"
    shift
    shift
    ;;
  port_forward | -pf)
    port_forward "$2"
    exit
    ;;
  install)
    install
    exit
    ;;
  delete)
    delete
    exit
    ;;
  help)
    show_help
    exit
    ;;
  *)
    log "${RED}Invalid option: $1"
    show_help
    exit 1
    ;;
  esac
done

if [[ -z "$NAME" || -z "$NAMESPACE" ]]; then
  log "${RED}Error: Missing required options."
  show_help
  exit 1
fi
