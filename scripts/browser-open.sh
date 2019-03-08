#!/bin/bash
#
#
# Open a web-browser pointing to the django web-app
# using the CLI tooling native to Mac/Linux. Attempt
# basic environment detection so we dont have to prompt

PLATFORM="$(uname -o)"

COMPOSE_ENV=dev
# If nginx is running, we are surely in prod-land, this obviously
# is not error free logic. Its possible for a user to clone this repo
# into a folder with a unique name which would cause a full grep
# to fail. :shrug:
( docker ps | grep -q _nginx_1 ) && export COMPOSE_ENV=prod

if [[ "${COMPOSE_ENV}" == "prod" ]]; then
    DOCKER_COMPOSE_FILE="ci-docker-compose.yaml"
    export CONTAINER="nginx"
    export PORT=8080
else
    DOCKER_COMPOSE_FILE="docker-compose.yaml"
    export CONTAINER="django"
    export PORT=8000
fi

export DJANGO_URL="http://$(docker-compose -f ${DOCKER_COMPOSE_FILE} port ${CONTAINER} ${PORT})"

# Are we on Linux?
if [[ "${PLATFORM,,}" == *"linux"* ]]; then
    xdg-open "${DJANGO_URL}" &
# I guess we are on Mac :shrug:
else
    open "${DJANGO_URL}" &
fi
