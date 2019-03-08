#!/bin/bash
# Container entrypoint script for Django applications.
set -e

wait_for_node() {
    if [ "${DEPLOY_ENV}" == "dev" ]; then
        echo "Waiting for node to start..." | json_format django-start.sh
        while [ ! -f .node_complete ]
        do
            sleep 2
        done
        rm -v .node_complete | json_format django-start.sh
    fi
}

wait_for_postgres() {
    echo "Waiting for postgres to start ..." | json_format django-start.sh
    until nc -z "${DJANGO_DB_HOST}" "${DJANGO_DB_PORT}"
    do
        sleep 2
    done
}

django_start() {
    if [ "${DJANGO_COLLECT_STATIC}" == "yes" ]; then
        ./manage.py collectstatic -c --noinput | json_format collectstatic
    fi
    ./manage.py migrate | json_format migrate
    if [ "${DEPLOY_ENV}" == "dev" ]; then
        ./manage.py runserver 0.0.0.0:8000
    else
        gunicorn -c /etc/gunicorn/gunicorn.py securethenews.wsgi
    fi
}

json_format() {
    MODULE="$1"
    LOGLEVEL="${2:-INFO}"
    DATE_EPOCH="$(date +'%s')"

    while read MESSAGE; do
        # append other fields, closing bracket
        # and a newline character
        JSON_STR="{ \"levelname\":\"${LOGLEVEL}\", \"message\":\"${MESSAGE}\", \"created\": \"${DATE_EPOCH}\", \"module\": \"${MODULE}\" }\n"

        printf "$JSON_STR"
    done

}

export -f json_format
wait_for_postgres
wait_for_node
django_start
