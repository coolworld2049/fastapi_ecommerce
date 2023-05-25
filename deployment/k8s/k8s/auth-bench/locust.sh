#!/usr/bin/env bash

set -euo pipefail

log() { printf '\n%s\n' "$1" >&2; }

NAMESPACE=fastapi-ecommerce

function port_forward() {
  kubectl port-forward --namespace "$NAMESPACE" svc/auth-service-locust 8089:8089 >/dev/null 2>&1 &
}

function install() {
  helm repo add deliveryhero https://charts.deliveryhero.io/ -n "$NAMESPACE"

  kubectl create configmap auth-service-loadtest-locustfile \
    --from-file ../../services/auth_service/auth_service_read/locustfile.py -n "$NAMESPACE"

  helm install auth-service-locust deliveryhero/locust \
    --set loadtest.name=auth-service-loadtest \
    --set loadtest.locust_locustfile=locustfile.py \
    --set loadtest.locust_locustfile_configmap=auth-service-loadtest-locustfile \
    -n "$NAMESPACE"
}

function delete() {
  helm uninstall auth-service-locust -n "$NAMESPACE"
  kubectl delete configmap auth-service-loadtest-locustfile -n "$NAMESPACE"
}

function show_help() {
  echo "Usage: $0 [OPTIONS]"
  echo "Options:"
  echo "  install         Install the auth-service-locust chart"
  echo "  -pf, port_forward    enable port forwarding"
  echo "  delete          Delete the auth-service-locust chart"
  echo "  help            Show this help message"
}

function main() {
  if [[ $# -eq 0 ]]; then
    log "Error: No action specified. Use 'install', 'delete', or 'help'."
    show_help
    exit 1
  fi

  case "$1" in
  install)
    install
    ;;
  delete)
    delete
    ;;
  -pf | port_forward)
    port_forward
    ;;
  help)
    show_help
    ;;
  *)
    log "Error: Unknown action: $1"
    show_help
    exit 1
    ;;
  esac
}

main "$@"
