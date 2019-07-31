#!/bin/bash

set -x

cd /django

if [[ -f ./manage.py ]]; then
    ./manage.py collectstatic -c --noinput
fi
