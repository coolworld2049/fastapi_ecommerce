#! /usr/bin/env bash

set -e

docker rm -f benchmark_vm

docker volume prune -f --filter "label!=keep"
