#!/bin/bash

exit_code=0

# Run django tests, we want to capture this exit code and fail but
# not stop the script right away
make app-tests-prod || exit_code=1

echo "--------------------------------------------------------------------------------------------------"
echo "                                     DEBUG                                                        "
echo "--------------------------------------------------------------------------------------------------"
docker-compose ps
echo "--------------------------------------------------------------------------------------------------"

# Copy XML from container into local environment
docker cp $(docker-compose ps -q django):/django-logs/app-tests.xml ./test-results/

# Run testinfra tests
make ops-tests || exit_code=1

exit "$exit_code"
