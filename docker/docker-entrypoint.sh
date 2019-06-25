#!/bin/bash
set -ex

./manage.py ensure_db_connection --wait 30

# TODO: As the migrations are not committed during the development phase, we
# make the migrations on runtime in docker-entrypoint.sh. To do this we chown
# the correct folder in Dockerfile. When the model have stabilized, the
# migrations should be comitted to the repository and these lines should be
# removed. See https://redmine.magenta-aps.dk/issues/30087
./manage.py makemigrations

./manage.py migrate

# See https://redmine.magenta-aps.dk/issues/30026 for changing this to a management command.
echo 'from bevillingsplatform.initialize import initialize;initialize()' | python manage.py shell

./manage.py collectstatic --no-input --clear

exec "$@"
