FROM quay.io/freedomofpress/ci-python

RUN apt-get update && apt-get install -y gcc libpq-dev paxctl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN adduser gcorn
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

EXPOSE 8000
USER gcorn
