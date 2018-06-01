FROM python:alpine3.6

COPY . /app
WORKDIR /app
RUN pip install .
ENTRYPOINT ["nexus_configurator"]
