#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALUES_FILE="${SCRIPT_DIR}/values.yaml"
RELEASE_NAME="auth-svc-pg"
NAMESPACE="fastapi-ecommerce"

RED='\033[0;31m'
GREEN='\033[0;32m'
#YELLOW='\033[0;33m'
NC='\033[0m' # No color

log() {
  local color=$1
  shift
  # shellcheck disable=SC2145
  echo -e "${color}$@${NC}"
}

apply_files_in_folder() {
  log "${GREEN}Apply *.yaml files..."
  local folder_path="$1"
  local color_red="\e[31m"
  local color_reset="\e[0m"

  if [ ! -d "$folder_path" ]; then
    echo -e "${color_red}Folder not found: $folder_path${color_reset}"
    echo "$(date) - Folder not found: $folder_path"
    return 1
  fi

  local files=("$folder_path"/*)
  if [ ${#files[@]} -eq 0 ]; then
    echo -e "${color_red}No files found in folder: $folder_path${color_reset}"
    echo "$(date) - No files found in folder: $folder_path"
    return 1
  fi

  for file in "${files[@]}"; do
    if [ -f "$file" ] && [[ "$file" = *.yaml* ]]; then
      kubectl apply -f "$file" -n "${NAMESPACE}"
    elif [ -f "$file" ] && [[ "$file" = *.conf* ]]; then
      kubectl create configmap "$(basename "$file")" --from-file="$file" -n "${NAMESPACE}"
    fi
  done
}

install_script() {
  apply_files_in_folder files
  log "${GREEN}Starting the script..."
  helm repo add bitnami https://charts.bitnami.com/bitnami
  helm install "${RELEASE_NAME}" -f "${VALUES_FILE}" oci://registry-1.docker.io/bitnamicharts/postgresql -n "${NAMESPACE}"
}

upgrade_helm_release() {
  apply_files_in_folder files
  log "${GREEN}Upgrading Helm release '${RELEASE_NAME}' in namespace '${NAMESPACE}'..."
  helm upgrade "${RELEASE_NAME}" -f "${VALUES_FILE}" oci://registry-1.docker.io/bitnamicharts/postgresql -n "${NAMESPACE}"
}

delete_script() {
  log "${RED}Stopping the script..."
  helm delete "${RELEASE_NAME}" -n "${NAMESPACE}"
}

port_forward_script() {
  if [[ "$PORT_FORWARD" == "true" ]]; then
    echo "Waiting for svc/${RELEASE_NAME}-postgresql-primary to start..."
    #sleep 5
    # POSTGRES_PASSWORD=$(kubectl get secret --namespace fastapi-ecommerce auth-svc-pg-postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)
    kubectl port-forward --namespace "${NAMESPACE}" svc/"${RELEASE_NAME}"-postgresql-primary 5432:5432 >/dev/null 2>&1 &
    #PGPASSWORD="$POSTGRES_PASSWORD" psql --host 127.0.0.1 -U postgres -d app -p 5432
    echo "Enabled"
  else
    log "${RED}Error: Port forwarding is not enabled. Use the 'port_forward' flag."
    show_help
    exit 1
  fi
}

show_help() {
  echo "Usage: script.sh [install|upgrade|delete|help] [OPTIONS]"
  echo "  install             Start the script"
  echo "  upgrade             Upgrade the Helm release"
  echo "  delete              Stop the script"
  echo "  help                Show help"
  echo ""
  echo "Options:"
  echo "  -r, --release        Release name"
  echo "  -n, --namespace      Namespace"
  echo "  -pf, --port_forward  Enable port forwarding"
}

while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
  install)
    install_script
    exit
    ;;
  upgrade)
    upgrade_helm_release
    exit
    ;;
  delete)
    delete_script
    exit
    ;;
  help)
    show_help
    exit
    ;;
  -r | --release)
    RELEASE_NAME="$2"
    shift
    shift
    ;;
  -n | --namespace)
    NAMESPACE="$2"
    shift
    shift
    ;;
  -pf | --port_forward)
    PORT_FORWARD="true"
    shift
    ;;
  *)
    log "${RED}Invalid option: $1"
    show_help
    exit 1
    ;;
  esac
done

if [[ -z "$RELEASE_NAME" || -z "$NAMESPACE" ]]; then
  log "${RED}Error: Missing required options."
  show_help
  exit 1
fi

if [[ -n "$PORT_FORWARD" ]]; then
  port_forward_script
else
  log "${RED}Error: No valid command provided."
  show_help
  exit 1
fi
