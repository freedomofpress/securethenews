#!/bin/ash
#

wait_for_node() {
    while [ ! -f .node_complete ]
    do
        sleep 2
    done
    rm -v .node_complete
}

django_start() {
    ./manage.py migrate && ./manage.py runserver 0.0.0.0:8000
}


wait_for_node
django_start
