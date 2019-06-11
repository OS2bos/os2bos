#!/bin/sh

sleep 5


#./manage.py flush --no-input
#./manage.py makemigrations
./manage.py migrate
./manage.py collectstatic --no-input --clear

exec "$@"
