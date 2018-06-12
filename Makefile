all: test
.PHONY: test all lint

nexus_configurator/groovy:
	./build.sh

test: nexus_configurator/groovy
	pytest -vv

lint:
	pylama
