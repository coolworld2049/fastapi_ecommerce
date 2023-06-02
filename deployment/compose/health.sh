#! /usr/bin/env bash


log() {
  printf '\n%s\n' "$1" >&2
}

check_and_install_package() {
  set +e
  local package="$1"
  log "Checking for $package..."
  if ! dpkg-query -W --showformat='${Status}\n' "$package" | grep -q "install ok installed"; then
    log "Package $package not found. Installing $package..."
    apt-get --yes install "$package"
  else
    log "Package $package is already installed."
  fi
  set -e
}

check_and_install_package "netcat"

ports=(27122-27130 27017 27119 6432 6434-6435 5432 5434-5435 443 80)
url="127.0.0.1"

for port in "${ports[@]}"; do
  if nc -vz -w 0 "$url" "$port"; then
    log "Port $port is open."
  else
    log "Port $port is closed."
    exit 1
  fi
done
