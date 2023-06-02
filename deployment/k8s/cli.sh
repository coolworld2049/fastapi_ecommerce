#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "${SCRIPT_DIR}"/../../.env

SCRIPT_DIR="${SCRIPT_DIR}"/k8s

PG_SERVICE_NAME=auth-postgresql
MONGO_SERVICE_NAME=store-mongo
NAMESPACE="${PROJECT_NAME:-fastapi-ecommerce}"

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
  log "${YELLOW}${action} *.yaml files in folder $folder_path, namespace: ${NAMESPACE} ...${NC}"
  local files=("$folder_path"/* "$folder_path"/.*)
  shopt -s nullglob
  for file in "${files[@]}"; do
    if [ -f "$file" ] && [[ "$file" = *.yaml ]] || [[ "$file" = *.yml ]] &&
      [[ "$file" != *example* ]] && ! [[ "$file" = *values*.yaml ]]; then
      if [ "$action" = "apply" ]; then
        kubectl apply -f "$file" -n "${NAMESPACE}"
      elif [ "$action" = "delete" ]; then
        kubectl delete -f "$file" -n "${NAMESPACE}"
      fi
    fi
  done
}

#-----------------------------

install_auth_postgresql() {
  log "\n${GREEN}Deploy auth-postgresql..."
  # bitnami postgres
  helm repo add bitnami https://charts.bitnami.com/bitnami
  kubectl apply -f "${SCRIPT_DIR}"/auth-postgresql/auth-postgresql-configmap.yaml -n "${NAMESPACE}"
  helm install "$PG_SERVICE_NAME" -f "${SCRIPT_DIR}/auth-postgresql/auth-postgresql-values.yaml" \
    oci://registry-1.docker.io/bitnamicharts/postgresql -n "${NAMESPACE}"

  #  # percona postgres operator
  #  path="${SCRIPT_DIR}"/auth-postgresql/percona-postgresql-operator
  #  [ -d "$path" ] || mkdir "$path"
  #  git clone -b v2.1.0 https://github.com/percona/percona-postgresql-operator "$path"
  #
  #  cd "$path" || log "${RED} ERROR"
  #  kubectl create namespace postgres-operator
  #  kubectl config set-context "$(kubectl config current-context)" --namespace=postgres-operator
  #  kubectl apply --server-side -f deploy/bundle.yaml
  #  kubectl apply -f deploy/cr.yaml
  #  cd "$(dirname "$path")" || log "${RED} ERROR"
  #
  #  log "${YELLOW}Get secrets..."
  #  sleep 3
  #  kubectl get secret cluster1-pguser-cluster1 --template='{{"user: "}}{{.data.user | base64decode}}{{"\npassword: "}}{{.data.password | base64decode}}'
  #  log "\n"
}

delete_auth_postgresql() {
  log "\n${GREEN}Deleting auth-postgresql..."

  # bitnami postgres
  kubectl delete -f "${SCRIPT_DIR}/auth-postgresql/auth-postgresql-configmap.yaml" -n "${NAMESPACE}"
  helm uninstall "$PG_SERVICE_NAME" -n "${NAMESPACE}"

  #  # percona postgres operator
  kubectl delete all --all -n postgres-operator
}

install_auth_postgresql_bench() {
  log "\n${GREEN}Deploy auth_postgresql_bench..."
  kubectl create configmap auth-postgresql-bench-configmap \
    --from-file="${SCRIPT_DIR}"/auth-postgresql-bench/scripts/pgbench.sh -n "${NAMESPACE}"
  process_files_in_folder apply "${SCRIPT_DIR}"/auth-postgresql-bench
}

delete_auth_postgresql_bench() {
  log "\n${GREEN}Delete auth_postgresql_bench..."
  kubectl delete configmap auth-postgresql-bench-configmap -n "${NAMESPACE}"
  process_files_in_folder delete "${SCRIPT_DIR}"/auth-postgresql-bench
}

install_auth() {
  log "\n${GREEN}Deploy auth..."
  process_files_in_folder apply "${SCRIPT_DIR}"/auth
}

delete_auth() {
  log "\n${GREEN}Delete auth..."
  process_files_in_folder delete "${SCRIPT_DIR}"/auth
}

#-----------------------------

install_store_mongo() {
  log "\n${GREEN}Deploy store-mongo..."
  helm install "$MONGO_SERVICE_NAME" -f "${SCRIPT_DIR}/store-mongo/store-mongo-values.yaml" \
    oci://registry-1.docker.io/bitnamicharts/mongodb -n "${NAMESPACE}"
}

delete_store_mongo() {
  log "\n${GREEN}Delete store-mongo..."
  helm delete "$MONGO_SERVICE_NAME" -n "${NAMESPACE}"
  process_files_in_folder delete "${SCRIPT_DIR}"/store-mongo
}

install_store() {
  log "\n${GREEN}Deploy store..."
  process_files_in_folder apply "${SCRIPT_DIR}"/store
}

delete_store() {
  log "\n${GREEN}Delete store..."
  process_files_in_folder delete "${SCRIPT_DIR}"/store
}

#-----------------------------

install_ingress_nginx() {
  log "\n${GREEN}Deploy ingress_nginx..."
  helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
  helm install ingress-nginx ingress-nginx/ingress-nginx -n "${NAMESPACE}"
  until process_files_in_folder apply "${SCRIPT_DIR}-${STAGE}"; do
    sleep 3
    log "${YELLOW}Try again${NC}"
  done
}

delete_ingress_nginx() {
  log "\n${GREEN}Delete ingress_nginx..."
  helm delete ingress-nginx -n "${NAMESPACE}"
  process_files_in_folder delete "${SCRIPT_DIR}-${STAGE}"
}

install_cert_manager() {
  log "\n${GREEN}Deploy cert_manager..."
  helm repo add jetstack https://charts.jetstack.io
  kubectl create namespace cert-manager
  kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.12.1/cert-manager.yaml
  until process_files_in_folder apply "${SCRIPT_DIR}"/issuer; do
    sleep 5
    log "${YELLOW}Try again${NC}"
  done
  echo -e "${GREEN}cert-manager has been installed successfully.${RESET}"
}

delete_cert_manager() {
  log "\n${GREEN}Delete cert_manager..."
  kubectl delete -f https://github.com/jetstack/cert-manager/releases/download/v1.12.1/cert-manager.yaml
  process_files_in_folder delete "${SCRIPT_DIR}"/issuer
  echo -e "${GREEN}cert-manager has been deleted successfully.${RESET}"
}

#-----------------------------

port_forward() {
  kubectl port-forward -n "${NAMESPACE}" svc/auth-postgresql-primary 5432:5432 &
  kubectl port-forward -n "${NAMESPACE}" svc/auth-postgresql-slave 5433:5433 &
}

install() {
  kubectl create namespace "${NAMESPACE}"

  install_auth_postgresql
  # install_auth_postgresql_bench
  install_auth

  install_store_mongo
  install_store

  install_ingress_nginx
  install_cert_manager

}

delete() {
  delete_auth_postgresql
  # delete_auth_postgresql_bench
  delete_auth

  delete_store_mongo
  delete_store

  delete_ingress_nginx
  delete_cert_manager

}

show_help() {
  echo "Usage: script.sh [install|upgrade|delete|help] [OPTIONS]"
  echo "  install                             Start the script"
  echo "  delete                              Stop the script"
  echo "  reinstall                              Stop and Start the script"
  echo "  -pf, port_forward                   Enable port forwarding"
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
  install)
    install
    exit
    ;;
  delete)
    delete
    exit
    ;;
  reinstall)
    delete
    install
    exit
    ;;
  -pf | port_forward)
    port_forward
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
