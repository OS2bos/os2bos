#!/bin/bash
# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

################################################################################
# Changes to this file requires approval from Labs. Please add a person from   #
# Labs as required approval to your MR if you have any changes.                #
################################################################################

set -ex

./manage.py ensure_db_connection --wait 30

if [ "$SKIP_MIGRATIONS" != "yes" ];
then
  # Run Migrate
  ./manage.py migrate
fi
# Initialize database if setting is True
./manage.py initialize_database

# Generate static content
./manage.py collectstatic --no-input --clear

exec "$@"
