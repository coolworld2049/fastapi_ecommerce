#! /bin/bash -x

set -e

cat /bitnami/postgresql/custom_conf/postgresql.conf >>/opt/bitnami/postgresql/conf/postgresql.conf
