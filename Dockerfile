FROM python:3.6-slim

COPY . /app
WORKDIR /app
RUN pip install .
USER nobody
ENTRYPOINT ["nexus_configurator"]
