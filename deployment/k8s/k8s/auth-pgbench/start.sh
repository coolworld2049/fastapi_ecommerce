#!/usr/bin/env bash

kubectl delete configmap auth-pgbench-configmap -n fastapi-ecommerce
kubectl create configmap auth-pgbench-configmap --from-file=scripts/pgbench.sh -n fastapi-ecommerce

kubectl delete -f auth-pgbench-depl.yaml
kubectl apply -f auth-pgbench-depl.yaml -n fastapi-ecommerce
