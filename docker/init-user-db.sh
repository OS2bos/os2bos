#!/bin/sh

# This file creates a database user. It can be mounted into the official
# postgres docker image (https://hub.docker.com/_/postgres) at
# `/docker-entrypoint-initdb.d/init-user-db.sh`. This is preferable to using the
# POSTGRES_* env variables as this user is not a SUPERUSER. A SUPERUSER can be
# used as privilege escalation to the postgres service system user in the event
# of SQL injection.

if [ -z "$DATABASE_NAME" ]; then echo "env var DATABASE_NAME is not set."; exit 1; fi
if [ -z "$DATABASE_USER" ]; then echo "env var DATABASE_USER is not set."; exit 1; fi
if [ -z "$DATABASE_PASSWORD" ]; then echo "env var DATABASE_PASSWORD is not set."; exit 1; fi

psql <<ENDSQL
CREATE DATABASE ${DATABASE_NAME};
CREATE USER bev WITH ENCRYPTED PASSWORD '${DATABASE_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE ${DATABASE_NAME} TO ${DATABASE_USER};
ENDSQL
