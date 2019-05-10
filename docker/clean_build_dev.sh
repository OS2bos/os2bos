#!/bin/bash

COMPOSE_FILE=${1:-compose-dev.yml}
PROJECT_NAME=${2:-dev}
OLD_NAME=${3:-${PROJECT_NAME}}

cd "$(dirname "$0")"

./clean.sh ${COMPOSE_FILE} ${OLD_NAME}
echo "-------------------"
echo "Building images."
echo "-------------------"
docker-compose -f ${COMPOSE_FILE} -p ${PROJECT_NAME} build

./initialize_dev.sh ${COMPOSE_FILE} ${PROJECT_NAME}

./run.sh ${COMPOSE_FILE} ${PROJECT_NAME}
