#!/bin/sh
# Copyright (C) 2015-2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# This file creates a database user. It can be mounted into the official
# postgres docker image (https://hub.docker.com/_/postgres) at
# `/docker-entrypoint-initdb.d/20-create-db-and-user.sh`. This is preferable to
# using the POSTGRES_* env variables as this user is not a SUPERUSER. A
# SUPERUSER can be used as privilege escalation to the postgres service system
# user in the event of SQL injection.

if [ -z "$DATABASE_NAME" ]; then echo "env var DATABASE_NAME is not set."; exit 1; fi
if [ -z "$DATABASE_USER" ]; then echo "env var DATABASE_USER is not set."; exit 1; fi
if [ -z "$DATABASE_PASSWORD" ]; then echo "env var DATABASE_PASSWORD is not set."; exit 1; fi

psql <<ENDSQL
CREATE DATABASE ${DATABASE_NAME};
CREATE USER ${DATABASE_USER} WITH ENCRYPTED PASSWORD '${DATABASE_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE ${DATABASE_NAME} TO ${DATABASE_USER};
ENDSQL
