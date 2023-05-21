#!/bin/bash

# Set the default release name and namespace
DEFAULT_RELEASE_NAME="my-release"
DEFAULT_NAMESPACE="default"

# Function to install the PostgreSQL HA chart
install_postgresql() {
  helm install "$RELEASE_NAME" oci://registry-1.docker.io/bitnamicharts/postgresql-ha \
    --namespace "$NAMESPACE"
}

# Function to delete the PostgreSQL HA release
delete_postgresql() {
  helm delete "$RELEASE_NAME" --namespace "$NAMESPACE"
}

# Function to display usage instructions
display_usage() {
  echo "Usage: $0 [--install|--delete|--help] [--name RELEASE_NAME] [--namespace NAMESPACE]"
  echo "  --install      : Install the PostgreSQL HA chart"
  echo "  --delete       : Delete the PostgreSQL HA release"
  echo "  --help         : Display usage instructions"
  echo "  --name         : Specify the release name (default: $DEFAULT_RELEASE_NAME)"
  echo "  --namespace    : Specify the namespace (default: $DEFAULT_NAMESPACE)"
  exit 1
}

# Set default values
RELEASE_NAME="$DEFAULT_RELEASE_NAME"
NAMESPACE="$DEFAULT_NAMESPACE"

# Process command line flags
while [[ $# -gt 0 ]]; do
  case $1 in
    --install)
      install_postgresql
      ;;
    --delete)
      delete_postgresql
      ;;
    --help)
      display_usage
      ;;
    --name)
      shift
      RELEASE_NAME="$1"
      ;;
    --namespace)
      shift
      NAMESPACE="$1"
      ;;
    *)
      echo "Invalid flag: $1"
      display_usage
      ;;
  esac
  shift
done
