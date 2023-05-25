#!/usr/bin/env bash

# Default values
DOCKER_USERNAME=""
DOCKER_PASSWORD=""
SRC_DIR="../src"
MAX_VERSIONS=1 # Maximum number of versions to keep

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
  echo "Builds and pushes Docker images to Docker Hub for each folder in the source directory that contains a Dockerfile."
  echo
  echo "Options:"
  echo "  -u, --username   Docker Hub username (required)"
  echo "  -p, --password   Docker Hub password (required)"
  echo "  -d, --directory  Source directory path (default: ../src)"
  echo "  -h, --help       Show help information"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
  -u | --username)
    DOCKER_USERNAME="$2"
    shift # past argument
    shift # past value
    ;;
  -p | --password)
    DOCKER_PASSWORD="$2"
    shift # past argument
    shift # past value
    ;;
  -d | --directory)
    SRC_DIR="$2"
    shift # past argument
    shift # past value
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
if [[ -z "$DOCKER_USERNAME" || -z "$DOCKER_PASSWORD" ]]; then
  echo "ERROR: Docker username and password are required."
  exit 1
fi

# Iterate through each folder in the source directory
for folder in "$SRC_DIR"/*/; do
  # Check if the folder contains a Dockerfile
  if [ -f "$folder/Dockerfile" ]; then
    # Extract the folder name
    folder_name=$(basename "$folder")

    # Login to Docker Hub
    log "${GREEN}" "Logging in to Docker Hub...${NC}"
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

    # Build the Docker image
    log "${GREEN}" "Building Docker image for $folder_name...${NC}"
    docker build -t "$folder_name" "$folder"

    ## Set initial version if it doesn't exist
    #latest_tag=$(curl -s "https://registry.hub.docker.com/v2/repositories/$DOCKER_USERNAME/$folder_name/tags/" |
    #  grep -o '"name":"[^"]*' | grep -o '[^"]*$' | sort -V | tail -n1)
    #log "${YELLOW}latest_tag=$latest_tag${NC}"
    #if [ -z "$latest_tag" ]; then
    #  current_version="1.0.0"
    #else
    #  current_version="$latest_tag"
    #fi
    #log "${YELLOW}current_version=$current_version${NC}"

    # Increment the Docker tag version
    # next_version=$(increment_version "$current_version" 2)
    next_version=latest
    log "${YELLOW}next_version=$next_version${NC}"

    # Tag the Docker image with the Docker Hub repository and version
    docker_tag="${DOCKER_USERNAME}/${folder_name}:${next_version}"
    docker tag "$folder_name" "$docker_tag"

    # Push the Docker image to Docker Hub
    log "${GREEN}" "Pushing Docker image to Docker Hub...${NC}"
    docker push "$docker_tag"

    # Delete old versions of the Docker image
    log "${GREEN}" "Deleting old versions of the Docker image...${NC}"
    docker images "${DOCKER_USERNAME}/${folder_name}" --format '{{.ID}} {{.Tag}}' |
      sort -rn | awk -v max_versions="$MAX_VERSIONS" 'NR > max_versions {print $1}' |
      xargs -r docker rmi -f

    # Logout from Docker Hub
    log "${GREEN}" "Logging out from Docker Hub...${NC}"
    docker logout
  fi
done
