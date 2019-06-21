#!/bin/bash

trap exit 1 SIGINT

MAX=30
for (( c=1; c<=$MAX; c++ )); do
    a=`printf %02d/%02d $c $MAX`
    if ./manage.py inspectdb > /dev/null 2>&1; then
        printf "$a Connected to database."
        break
    elif [ $c -ge $MAX ]; then
        echo "$a Unable to connect to database. Giving up."
        exit 1
    fi
    echo "$a Unable to connect to database."
    sleep 1;
done;

# TODO: As the migrations are not committed during the development phase, we
# make the migrations on runtime in docker-entrypoint.sh. To do this we chown
# the correct folder in Dockerfile. When the model have stabilized, the
# migrations should be comitted to the repository and these lines should be
# removed. See https://redmine.magenta-aps.dk/issues/30087
echo "[docker-compose] manage.py makemigrations"
./manage.py makemigrations

echo "[docker-compose] manage.py  migrate"
./manage.py migrate

# See https://redmine.magenta-aps.dk/issues/30026 for changing this to a management command.
echo "[docker-compose] manage.py initialize"
echo 'from bevillingsplatform.initialize import initialize;initialize()' | python manage.py shell


echo "[docker-compose] manage.py collectstatic"
./manage.py collectstatic --no-input --clear

exec "$@"
