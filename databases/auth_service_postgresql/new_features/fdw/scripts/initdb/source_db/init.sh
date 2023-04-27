#! /usr/bin/env bash

export PGPASSWORD="${POSTGRES_PASSWORD? env required}"

psql -U "$POSSTGRES_USERNAME" -d postgres -ea \
  -c 'drop database source_db;' \
  -c 'create database source_db;'
