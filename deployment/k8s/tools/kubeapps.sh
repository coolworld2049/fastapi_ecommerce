#!/usr/bin/env bash

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

install_kubeapps() {
  helm repo add bitnami https://charts.bitnami.com/bitnami
  kubectl create namespace kubeapps
  helm install kubeapps --namespace kubeapps bitnami/kubeapps

  kubectl create --namespace default serviceaccount kubeapps-operator
  kubectl create clusterrolebinding kubeapps-operator --clusterrole=cluster-admin --serviceaccount=default:kubeapps-operator
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

port_forward() {
  echo -e "\n"
  if [[ "$platform" == "linux" ]]; then
    kubectl get --namespace default secret kubeapps-operator-token -o go-template='{{.data.token | base64decode}}'
  elif [[ "$platform" == "win" ]]; then
    powershell -Command "[Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String(\$(kubectl get --namespace default secret kubeapps-operator-token -o jsonpath='{.data.token}')))"
  fi
  echo -e "\n"

  count=0
  trap "exit" INT # Trap Ctrl-C signal and exit gracefully
  until kubectl port-forward -n kubeapps svc/kubeapps 8080:80; do
    echo "Try again $count"
    sleep 3
    count=$((count + 1))
    if [ "$count" -ge 5 ]; then
      break
    fi
  done
}

delete_kubeapps() {
  helm uninstall -n kubeapps kubeapps
  kubectl delete namespace kubeapps
  kubectl delete clusterrolebinding kubeapps-operator
  kubectl delete serviceaccount kubeapps-operator -n default
  kubectl delete secret kubeapps-operator-token -n default
}

print_help() {
  echo "Usage: ./kubeapps.sh [OPTION]"
  echo "Options:"
  echo "  -i, --install       Install Kubeapps"
  echo "  -d, --delete        Delete Kubeapps"
  echo "  -pf,--port-forward  Port forward"
  echo "  -h, --help          Print this help message"
}

# Parse command line options
while [[ "$#" -gt 0 ]]; do
  case $1 in
  -i | --install)
    install_kubeapps
    exit 0
    ;;
  -d | --delete)
    delete_kubeapps
    exit 0
    ;;
  -pf | --port-forward)
    port_forward
    exit 0
    ;;
  -h | --help)
    print_help
    exit 0
    ;;
  *)
    echo "Invalid option: $1"
    print_help
    exit 1
    ;;
  esac
  shift
done

# If no options provided, print help message
print_help
exit 0
