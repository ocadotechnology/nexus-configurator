FROM python:alpine3.6

COPY . /app
WORKDIR /app
RUN pip install pipenv && pipenv install
ENV SHELL=/bin/sh
ENTRYPOINT ["pipenv", "run", "nexus_configurator"]
