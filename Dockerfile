FROM alpine:3.7
COPY build.sh /tmp
WORKDIR /tmp
RUN mkdir -p /tmp/nexus_configurator/groovy && \
    apk update && \
    apk add curl && \
    ./build.sh

FROM python:3.6-slim
COPY . /app
WORKDIR /app
COPY --from=0 /tmp/nexus_configurator/groovy /app/nexus_configurator/groovy
RUN pip install .
USER nobody
ENTRYPOINT ["nexus_configurator"]
