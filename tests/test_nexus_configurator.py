from pkg_resources import resource_filename
import sys
from unittest import mock
from unittest.mock import patch

from nexus_configurator.nexus import NexusUnauthorised
import nexus_configurator.nexus_configurator as nexus_configurator

SAMPLE_CONFIG = [{'setup_anonymous_access': [{'anonymous_access': True}]}]
SAMPLE_CONFIG_PATH = 'tests/test_data/example_config.yaml'
GROOVY_SCRIPTS_DIR = resource_filename("nexus_configurator", "groovy")


@mock.patch('nexus_configurator.nexus_configurator.Nexus')
def test_nexus_sets_up_anonymous_access(nexus):
    anon_access_script = GROOVY_SCRIPTS_DIR + '/setup_anonymous_access.groovy'
    testargs = ["nexus_configurator",
                "--config",
                SAMPLE_CONFIG_PATH]
    with patch.object(sys, 'argv', testargs):
        nexus_configurator.main()

    nexus().create_script.assert_any_call(anon_access_script)
    nexus().run_script.assert_any_call('setup_anonymous_access',
                                       anonymous_access=True)


@mock.patch('nexus_configurator.nexus_configurator.Nexus')
def test_nexus_auth_tries_each_password_until_successful(nexus):
    testargs = ["nexus_configurator",
                "--config",
                SAMPLE_CONFIG_PATH,
                "-c",
                "tests/test_data/test_auth"]
    passwords = ['admin123', 'admin12345', 'pass2', 'pass3']
    nexus.side_effect = [NexusUnauthorised(),
                         NexusUnauthorised(),
                         NexusUnauthorised(),
                         nexus()]
    with patch.object(sys, 'argv', testargs):
        nexus_configurator.main()
    for p in passwords:
        nexus.assert_any_call(host='http://localhost:8081',
                              password=p,
                              user='admin')
