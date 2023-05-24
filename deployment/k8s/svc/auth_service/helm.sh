#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="auth-service"
PG_SERVICE_NAME="$SERVICE_NAME"-postgresql
VALUES_FILE="${SCRIPT_DIR}/postgresql/values.yaml"
NAMESPACE="fastapi-ecommerce"

RED='\033[0;31m'
GREEN='\033[0;32m'
#YELLOW='\033[0;33m'
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
  log "${GREEN}${action} *.yaml files in folder $folder_path ..."

  local files=("$folder_path"/* "$folder_path"/.*)
  shopt -s nullglob
  for file in "${files[@]}"; do
    if [ -f "$file" ] && [[ "$file" = *.yaml ]] && [[ "$file" != *example* ]]; then
      if [ "$action" = "apply" ]; then
        kubectl apply -f "$file" -n "${NAMESPACE}"
      elif [ "$action" = "delete" ]; then
        kubectl delete -f "$file" -n "${NAMESPACE}"
      fi
    fi
  done
}

install() {
  log "${GREEN}Deploy auth-service-postgresql..."
  process_files_in_folder apply postgresql/files
  helm repo add bitnami https://charts.bitnami.com/bitnami
  helm install "$PG_SERVICE_NAME" -f "${VALUES_FILE}" oci://registry-1.docker.io/bitnamicharts/postgresql -n "${NAMESPACE}"

  log "${GREEN}Deploy auth-service..."
  process_files_in_folder apply app/files
}

upgrade() {
  process_files_in_folder apply files
  log "${GREEN}Upgrading Helm release '${SERVICE_NAME}' in namespace '${NAMESPACE}'..."
  helm upgrade "$PG_SERVICE_NAME" -f "${VALUES_FILE}" oci://registry-1.docker.io/bitnamicharts/postgresql -n "${NAMESPACE}"
}

delete() {
  log "${RED}Stopping the script..."
  helm delete "$PG_SERVICE_NAME" -n "${NAMESPACE}"
  process_files_in_folder delete postgresql/files
  process_files_in_folder delete app/files
}

port_forward() {
  local service_name="$1"

  case "$service_name" in
  auth-service)
    kubectl port-forward --namespace "${NAMESPACE}" "svc/${service_name}" 80:80 &
    echo "Port forwarding enabled for service ${service_name}"
    ;;
  auth-service-postgresql)
    kubectl port-forward --namespace "${NAMESPACE}" "svc/${service_name}-primary" 5432:5432 &
    kubectl port-forward --namespace "${NAMESPACE}" "svc/${service_name}-slave" 5433:5433 &
    echo "Port forwarding enabled for service ${service_name} (primary and slave)"
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
  echo "  upgrade                             Upgrade the Helm release"
  echo "  delete                              Stop the script"
  echo "  port_forward, -pf <service_name>    Enable port forwarding"
  echo "  help                                Show help"
  echo ""
  echo "Options:"
  echo "  -r, --release                       Release name"
  echo "  -n, --namespace                     Namespace"
}

while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
  -r | --release)
    SERVICE_NAME="$2"
    shift
    shift
    ;;
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
  upgrade)
    upgrade
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
