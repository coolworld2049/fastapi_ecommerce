#!/usr/bin/env bash

kubectl create configmap pgbench-config --from-file=scripts/pgbench.sh -n fastapi-ecommerce
kubectl apply -f pgbench-vm.yaml -n fastapi-ecommerce
