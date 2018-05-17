#!/bin/ash
#

wait_for_node() {
    if [ "${DEPLOY_ENV}" != "prod" ]; then
        echo Waiting for node to start..
        while [ ! -f .node_complete ]
        do
            sleep 2
        done
        rm -v .node_complete
    fi
}

wait_for_postgres() {
    echo Waiting for postgres to start..
    wait-for-it.sh -t 120 -h ${DJANGO_DB_HOST} -p ${DJANGO_DB_PORT}
}

django_start() {
    if [ "${DEPLOY_ENV}" == "prod" ]; then
        ./manage.py migrate
        ./manage.py collectstatic -c --noinput
        gunicorn -c /etc/gunicorn/gunicorn.py securethenews.wsgi
    else
        ./manage.py migrate && ./manage.py runserver 0.0.0.0:8000
    fi
}


wait_for_postgres
wait_for_node
django_start
