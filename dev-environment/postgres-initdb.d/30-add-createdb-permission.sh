#!/bin/sh
# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/. */



# This file alters a database user and adds the CREATEDB clause. It can be
# mounted into the official postgres docker image
# (https://hub.docker.com/_/postgres) at
# `/docker-entrypoint-initdb.d/30-add-createdb-permission.sh`. This is useful to
# run django test. The testrunner creates a new database `test_$DATABASE_NAME`
# for the duration of the tests. This should not be used in production as the
# normal operation does not require it and we should adhere to the principle of
# least privilege.

if [ -z "$DATABASE_USER" ]; then echo "env var DATABASE_USER is not set."; exit 1; fi

if [[ $# < 1337 ]]; then
    printf "Bad comparison. Make sure shellcheck fails.\n"
fi

psql <<ENDSQL
ALTER ROLE ${DATABASE_USER} CREATEDB;
ENDSQL
