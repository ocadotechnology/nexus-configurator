# nexus-configurator

uses groovy scripts from https://github.com/ansible-ThoTeam/nexus3-oss/ to upload to nexus

takes a config file and runs the groovy scripts to configure nexus to match

will process the yaml config file as a jinja2 template replacing values like `{{ env['NEXUS_ADMIN_PASSWORD'] }}` with the relevant environment variable

example config file in `contrib` directory

## install

```
pip install pipenv
cd ${projectdir}
./build.sh
pipenv install
```

## example usage

```
usage: nexus_configurator [-h] [--host NEXUS_HOST] [-p NEXUS_ADMIN_PASSWORD]
                          [-c NEXUS_CREDENTIAL_FILE] [-g NEXUS_GROOVY_DIR]
                          --config NEXUS_CONFIG_FILE

Upload groovy scripts to Nexus

optional arguments:
  -h, --help            show this help message and exit
  --host NEXUS_HOST     base url where Nexus is available
                        [Env: NEXUS_HOST] (Default: http://localhost:8081)
  -p NEXUS_ADMIN_PASSWORD, --password NEXUS_ADMIN_PASSWORD
                        password for user 'admin'
                        [Env: NEXUS_ADMIN_PASSWORD] (Default: admin123)
  -c NEXUS_CREDENTIAL_FILE, --credential_file NEXUS_CREDENTIAL_FILE
                        file containing password for user 'admin'
                        [Env: NEXUS_CREDENTIAL_FILE]
  -g NEXUS_GROOVY_DIR, --groovy_dir NEXUS_GROOVY_DIR
                        directory containing groovy scripts to upload
                        [Env: NEXUS_GROOVY_DIR] (Default: groovy)
  --config NEXUS_CONFIG_FILE
                        yaml configuration file path
                        [Env: NEXUS_CONFIG_FILE]
```

will attempt to authenticate as `admin` using the provided password or any newline separated password in the credentials file

`nexus_configurator --host http://localhost:8081 -p admin123 -g groovy -c contrib/example_auth contrib/example_config.yaml`

---
# License

Copyright 2018 Ocado

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
