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


#./manage.py flush --no-input
#./manage.py makemigrations
./manage.py migrate
./manage.py collectstatic --no-input --clear

exec "$@"
