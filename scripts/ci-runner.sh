#!/bin/bash

set -x

exit_code=0

# Run django tests, we want to capture this exit code and fail but
# not stop the script right away
make app-tests-prod || exit_code=1

# get django container ID
DJANGO_CONTAINER_ID=$(docker-compose ps -q django)

if [ -z "${DJANGO_CONTAINER_ID}" ]; then
    echo "Django container failed to start, bailing out!"
    exit_code=-1
else
    # Copy XML from container into local environment
    docker cp ${DJANGO_CONTAINER_ID}:/django-logs/app-tests.xml ./test-results/

    # Run testinfra tests
    make ops-tests || exit_code=1
fi

exit "$exit_code"
