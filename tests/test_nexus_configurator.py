import base64
from pkg_resources import resource_filename
import sys
from unittest import mock
from unittest.mock import patch

import boto3
import httpretty
from moto import mock_s3

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


@mock_s3
def test_read_config_file_from_s3():
    bucket_name = 'config_bucket'
    s3_key = 'configfilename'

    s3_client = boto3.client('s3')
    s3_client.create_bucket(Bucket=bucket_name)
    with open(SAMPLE_CONFIG_PATH) as f:
        body = f.read()

    s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=body)

    s3_url = 's3://' + bucket_name + '/' + s3_key
    config = nexus_configurator.read_config_file(s3_url)
    assert(config == SAMPLE_CONFIG)


def test_read_config_file_from_disk():
    config_file_path = SAMPLE_CONFIG_PATH
    config = nexus_configurator.read_config_file(config_file_path)
    assert(config == SAMPLE_CONFIG)


@httpretty.activate
def test_read_config_file_from_http_with_auth():
    config_url = 'http://someuser:somepass@configserver.bar/config'
    with open(SAMPLE_CONFIG_PATH) as f:
        body = f.read()
    httpretty.register_uri(
        httpretty.GET,
        config_url,
        body=body
    )
    config = nexus_configurator.read_config_file(config_url)
    assert(httpretty.last_request().headers['Authorization'] ==
           'Basic ' + base64.b64encode(b'someuser:somepass').decode())
    assert(config == SAMPLE_CONFIG)
