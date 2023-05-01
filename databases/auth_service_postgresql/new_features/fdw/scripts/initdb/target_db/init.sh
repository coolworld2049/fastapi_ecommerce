#! /usr/bin/env bash

export PGPASSWORD="${POSTGRES_PASSWORD? env required}"

psql -U "$POSSTGRES_USERNAME" -d postgres -ea \
  -c 'drop database target_db;' \
  -c 'create database target_db;'
