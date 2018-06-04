#!/bin/sh

release="v2.1.2"
rm -rf nexus3-*
rm -rf nexus_configurator/groovy
curl -L https://github.com/ansible-ThoTeam/nexus3-oss/archive/${release}.tar.gz | tar xz
mv nexus3-* nexus3-oss
ln -s ../nexus3-oss/files/groovy nexus_configurator/groovy
