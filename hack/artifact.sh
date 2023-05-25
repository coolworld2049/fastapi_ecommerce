#!/usr/bin/env bash

# Default values
USERNAME=""
PASSWORD=""
SRC_DIR="../src"
MAX_VERSIONS=1 # Maximum number of versions to keep
PYPI_UPLOAD=false
DOCKER_BUILD=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"/k8s

# RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Function to increase the version
increment_version() {
  local version=$1
  local part=$2
  local next_version

  IFS='.' read -ra version_parts <<<"$version"

  # Increment the specified part
  # shellcheck disable=SC2004
  version_parts[$part]=$((version_parts[$part] + 1))

  # Reset lower parts to 0
  # shellcheck disable=SC2004
  for ((i = $part + 1; i < 3; i++)); do
    version_parts[$i]=0
  done

  next_version="${version_parts[0]}.${version_parts[1]}.${version_parts[2]}"
  echo "$next_version"
}

# Function for colorized logging
log() {
  local color=$1
  shift
  # shellcheck disable=SC2145
  echo -e "${color}$@${NC}"
}

# Function to display usage instructions
show_help() {
  echo "Usage: ./script.sh [OPTIONS]"
  echo "Docker builds and pushes Docker images to Docker Hub for each folder in the source directory that contains a Dockerfile."
  echo
  echo "Options:"
  echo "  -u, --username   Docker Hub or PyPI username (required)"
  echo "  -p, --password   Docker Hub or PyPI password (required)"
  echo "  -d, --directory  Source directory path (default: ../src)"
  echo "  --pypi           Upload package to PyPI"
  echo "  --docker         Docker builds Docker images"
  echo "  -h, --help       Show help information"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
  -u | --username)
    USERNAME="$2"
    shift # past argument
    shift # past value
    ;;
  -p | --password)
    PASSWORD="$2"
    shift # past argument
    shift # past value
    ;;
  -d | --directory)
    SRC_DIR="$2"
    shift # past argument
    shift # past value
    ;;
  --pypi)
    PYPI_UPLOAD=true
    shift # past argument
    ;;
  --docker)
    DOCKER_BUILD=true
    shift # past argument
    ;;
  -h | --help)
    show_help
    exit 0
    ;;
  *) # unknown option
    echo "ERROR: Unknown option: $key"
    show_help
    exit 1
    ;;
  esac
done

# Check if required flags are provided
if [[ -z "$USERNAME" || -z "$PASSWORD" ]]; then
  echo "ERROR: Docker username and password are required."
  exit 1
fi

# Upload package to PyPI if --pypi flag is provided
if [[ -d "$SRC_DIR"/core && "$PYPI_UPLOAD" == true ]]; then
  path="$SRC_DIR"/core/fastapi_ecommerce_core
  FILE_PATH="$path"/setup.py
  CURRENT_VERSION=0.3.6
  NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. -v OFS=. '{$NF++;print}')
  sed -i "s/$CURRENT_VERSION/$NEW_VERSION/g" "$FILE_PATH"
  sed -i "s/$CURRENT_VERSION/$NEW_VERSION/g" "$PWD"/artifact.sh
  log "${GREEN}Version updated from $CURRENT_VERSION to $NEW_VERSION in $FILE_PATH ${NC}"
  log "${GREEN}" "Uploading package to PyPI...${NC}"
  # shellcheck disable=SC2164
  cd "$SRC_DIR"/core
  bash publish.sh "$USERNAME" "$PASSWORD"
  # shellcheck disable=SC2164
  cd "$SCRIPT_DIR"
fi

# Iterate through each folder in the source directory
for folder in "$SRC_DIR"/*/; do
  # Check if the folder contains a Dockerfile
  if [[ -f "$folder/Dockerfile" && "$DOCKER_BUILD" == true ]]; then
    # Extract the folder name
    folder_name=$(basename "$folder")

    # Login to Docker Hub
    log "${GREEN}" "Logging in to Docker Hub...${NC}"
    echo "$PASSWORD" | docker login -u "$USERNAME" --password-stdin

    # Docker build the Docker image
    log "${GREEN}" "Docker building Docker image for $folder_name...${NC}"
    docker build -t "$folder_name" "$folder"

    # Increment the Docker tag version
    next_version=latest
    log "${YELLOW}next_version=$next_version${NC}"

    # Tag the Docker image with the Docker Hub repository and version
    tag="${USERNAME}/${folder_name}:${next_version}"
    docker tag "$folder_name" "$tag"

    # Push the Docker image to Docker Hub
    log "${GREEN}" "Pushing Docker image to Docker Hub...${NC}"
    docker push "$tag"

    # Delete old versions of the Docker image
    log "${GREEN}" "Deleting old versions of the Docker image...${NC}"
    docker images "${USERNAME}/${folder_name}" --format '{{.ID}} {{.Tag}}' |
      sort -rn | awk -v max_versions="$MAX_VERSIONS" 'NR > max_versions {print $1}' |
      xargs -r docker rmi -f

    # Logout from Docker Hub
    log "${GREEN}" "Logging out from Docker Hub...${NC}"
    docker logout
  fi
done
