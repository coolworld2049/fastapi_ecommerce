#!/bin/bash

platform=""

# Detect the platform
unameOut="$(uname -s)"
case "${unameOut}" in
Linux*) platform="linux" ;;
Darwin*) platform="mac" ;;
CYGWIN*) platform="win" ;;
MINGW*) platform="win" ;;
*) platform="unknown" ;;
esac

if [[ "$platform" == "unknown" ]]; then
  echo -e "\e[91mUnknown platform: $unameOut\e[0m"
  exit 1
fi

# Color variables
# RED='\e[91m'
GREEN='\e[92m'
# YELLOW='\e[93m'
RESET='\e[0m'

install_cert_manager() {
  kubectl apply --validate=false -f \
    https://github.com/jetstack/cert-manager/releases/download/v1.9.1/cert-manager.crds.yaml

  kubectl create namespace cert-manager

  helm repo add jetstack https://charts.jetstack.io
  helm repo update

  helm install cert-manager --namespace cert-manager jetstack/cert-manager

  echo -e "${GREEN}cert-manager has been installed successfully.${RESET}"
}

delete_cert_manager() {
  # Delete the cert-manager release
  helm delete cert-manager -n cert-manager

  # Delete the cert-manager namespace
  kubectl delete namespace cert-manager

  echo -e "${GREEN}cert-manager has been deleted successfully.${RESET}"
}



display_help() {
  echo "Usage: $0 [option]"
  echo "Options:"
  echo "  install       - Install cert-manager and Scaffold."
  echo "  delete        - Delete cert-manager and Scaffold."
  echo "  -h, help      - Display this help message."
}

case "$1" in
install)
  install_cert_manager
  ;;
delete)
  delete_cert_manager
  ;;
-h | help)
  display_help
  ;;
*)
  display_help
  exit 1
  ;;
esac
