#!/bin/bash

COMPOSE_FILE=${1:-compose-dev.yml}
PROJECT_NAME=${2:-dev}

cd "$(dirname "$0")"

echo "------------------------"
echo "Initializing containers."
echo "------------------------"
docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} up --no-start
docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} start db
