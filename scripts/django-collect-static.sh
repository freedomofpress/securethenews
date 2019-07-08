#!/bin/bash

set -x

cd /django

if [[ -f .env ]]; then
    . .env
fi

env

if [[ -f ./manage.py ]]; then
    ./manage.py collectstatic -c --noinput
fi
