#!/bin/bash

set -x

cd /django

if [[ -f .env.prod ]]; then
    . .env.prod
fi

env

if [[ -f ./manage.py ]]; then
    ./manage.py collectstatic -c --noinput
fi
