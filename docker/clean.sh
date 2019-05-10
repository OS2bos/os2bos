#!/bin/bash

COMPOSE_FILE=${1:-compose-dev.yml}
PROJECT_NAME=${2:-dev}

cd "$(dirname "$0")"

echo "--------------------------------"
echo "Taking down existing containers."
echo "--------------------------------"
docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} down
echo "---------------------------------------"
echo "Removing database container and volume."
echo "---------------------------------------"
docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} rm db
docker volume rm ${PROJECT_NAME}_postgres_data
./wipe_generated.sh
