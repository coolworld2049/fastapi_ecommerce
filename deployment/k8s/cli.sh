#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "${SCRIPT_DIR}"/../../.env

if [ "$STAGE" == 'test' ]; then
  STAGE=dev
fi

SCRIPT_DIR="${SCRIPT_DIR}"/k8s
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

process_dir_files() {
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
  log "\n${GREEN}Deploy auth_postgresql..."
  helm repo add bitnami https://charts.bitnami.com/bitnami
  kubectl apply -f "${SCRIPT_DIR}"/auth-postgresql/auth-postgresql-configmap.yaml -n "${NAMESPACE}"
  helm install auth-postgresql -f "${SCRIPT_DIR}/auth-postgresql/auth-postgresql-values.yaml" -n "${NAMESPACE}" \
    oci://registry-1.docker.io/bitnamicharts/postgresql

}

delete_auth_postgresql() {
  log "\n${GREEN}Delete auth_postgresql..."
  kubectl delete -f "${SCRIPT_DIR}/auth-postgresql/auth-postgresql-configmap.yaml" -n "${NAMESPACE}"
  helm delete auth-postgresql -n "${NAMESPACE}"
}

install_auth_postgresql_bench() {
  log "\n${GREEN}Deploy auth_postgresql_bench..."
  kubectl create configmap auth-postgresql-bench-configmap \
    --from-file="${SCRIPT_DIR}"/auth-postgresql-bench/scripts/pgbench.sh -n "${NAMESPACE}"
  process_dir_files apply "${SCRIPT_DIR}"/auth-postgresql-bench
}

delete_auth_postgresql_bench() {
  log "\n${GREEN}Delete auth_postgresql_bench..."
  kubectl delete configmap auth-postgresql-bench-configmap -n "${NAMESPACE}"
  process_dir_files delete "${SCRIPT_DIR}"/auth-postgresql-bench
}

install_auth() {
  log "\n${GREEN}Deploy auth..."
  process_dir_files apply "${SCRIPT_DIR}"/auth
}

delete_auth() {
  log "\n${GREEN}Delete auth..."
  process_dir_files delete "${SCRIPT_DIR}"/auth
}

#-----------------------------

install_store_mongo() {
  log "\n${GREEN}Deploy store-mongo..."
  helm install store-mongo -f "${SCRIPT_DIR}/store-mongo/store-mongo-values.yaml" \
    oci://registry-1.docker.io/bitnamicharts/mongodb -n "${NAMESPACE}"
}

delete_store_mongo() {
  log "\n${GREEN}Delete store-mongo..."
  helm delete store-mongo -n "${NAMESPACE}"
  process_dir_files delete "${SCRIPT_DIR}"/store-mongo
}

install_store() {
  log "\n${GREEN}Deploy store..."
  process_dir_files apply "${SCRIPT_DIR}"/store
}

delete_store() {
  log "\n${GREEN}Delete store..."
  process_dir_files delete "${SCRIPT_DIR}"/store
}

#-----------------------------

install_ingress_nginx() {
  log "\n${GREEN}Deploy ingress_nginx..."
  helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
  helm install ingress-nginx ingress-nginx/ingress-nginx -n "${NAMESPACE}"
}

delete_ingress_nginx() {
  log "\n${GREEN}Delete ingress_nginx..."
  helm delete ingress-nginx -n "${NAMESPACE}"
}

install_cert_manager() {
  log "\n${GREEN}Deploy cert_manager..."
  kubectl create namespace cert-manager
  kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.12.1/cert-manager.yaml
}

delete_cert_manager() {
  log "\n${GREEN}Delete cert_manager..."
  kubectl delete -f https://github.com/jetstack/cert-manager/releases/download/v1.12.1/cert-manager.yaml
}

#-----------------------------

install_kubeapps() {
  helm repo add bitnami https://charts.bitnami.com/bitnami
  kubectl create namespace kubeapps
  helm install kubeapps --namespace kubeapps bitnami/kubeapps
  kubectl create --namespace default serviceaccount kubeapps-operator
  kubectl create clusterrolebinding kubeapps-operator \
    --clusterrole=cluster-admin \
    --serviceaccount=default:kubeapps-operator
  cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: kubeapps-operator-token
  namespace: default
  annotations:
    kubernetes.io/service-account.name: kubeapps-operator
type: kubernetes.io/service-account-token
EOF
}

delete_kubeapps() {
  helm uninstall -n kubeapps kubeapps
  kubectl delete namespace kubeapps
  kubectl delete clusterrolebinding kubeapps-operator
  kubectl delete serviceaccount kubeapps-operator -n default
  kubectl delete secret kubeapps-operator-token -n default
}

#-----------------------------

install_monitoring() {
  log "\n${GREEN}Deploy monitoring..."

  helm repo add percona https://percona.github.io/percona-helm-charts/
  helm install pmm --set service.type="LoadBalancer" percona/pmm -n "${NAMESPACE}" \
    -f "${SCRIPT_DIR}"/monitoring/pmm-values.yaml
}

delete_monitoring() {
  log "\n${GREEN}Delete monitoring..."

  helm delete pmm -n "${NAMESPACE}"
}

#-----------------------------

install_backup_tools() {
  log "\n${GREEN}Deploy backup_tools..."

}

delete_backup_tools() {
  log "\n${GREEN}Delete backup_tools..."

}

install() {
  kubectl create namespace "${NAMESPACE}"
  install_auth_postgresql
  # install_auth_postgresql_bench
  install_auth
  install_store_mongo
  install_store
  install_monitoring
  #  install_backup_tools
}

delete() {
  delete_auth_postgresql
  delete_auth_postgresql_bench
  delete_auth
  delete_store_mongo
  delete_store
  delete_monitoring
  delete_backup_tools
}

#-----------------------------

install_ingress_network() {
  install_ingress_nginx
  install_cert_manager
}

delete_ingress_network() {
  delete_ingress_nginx
  delete_cert_manager
  process_dir_files delete "${SCRIPT_DIR}-${STAGE}"
}

show_help() {
  echo "Usage: script.sh [install|upgrade|delete|help] [OPTIONS]"
  echo "  install                             Start the script"
  echo "  install-ingress-net                 Start the script"
  echo "  delete                              Stop the script"
  echo "  delete-ingress-net                  Start the script"
  echo "  reinstall                           Stop and Start the script"
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
  install-ingress-net)
    install_ingress_network
    until kubectl apply -f "${SCRIPT_DIR}-${STAGE}/issuer.yaml" -n "$NAMESPACE"; do
      log "${YELLOW}Try again${NC}"
      sleep 5
    done
    until kubectl apply -f "${SCRIPT_DIR}-${STAGE}/ingress.yaml" -n "$NAMESPACE"; do
      log "${YELLOW}Try again${NC}"
      sleep 5
    done
    exit
    ;;
  delete)
    delete
    exit
    ;;
  delete-ingress-net)
    delete_ingress_network
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
