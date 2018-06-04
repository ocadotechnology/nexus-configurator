#!/usr/bin/env python3
import argparse
import glob
import jinja2
import json
import os
import os.path
from pkg_resources import resource_filename
import sys
import yaml
from nexus_configurator.nexus import Nexus, NexusUnauthorised, NexusConnectionError

ADMIN_USER = "admin"
GROOVY_SCRIPTS_DIR = resource_filename("nexus_configurator", "groovy")


class EnvDefault(argparse.Action):
    """
    add custom action to accept environment variables as
    default values and append details to help output
    """
    def __init__(self, envvar, required=True,
                 default=None, help=None, **kwargs):
        if envvar in os.environ:
            default = os.environ.get(envvar)
        if required and default:
            required = False
        help = "{}\n[Env: {}]".format(help, envvar)
        if default:
            help = "{} (Default: {})".format(help, default)
        super(EnvDefault, self).__init__(default=default, required=required,
                                         metavar=envvar, help=help, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Upload groovy scripts to Nexus',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--host",
                        help="base url where Nexus is available",
                        default="http://localhost:8081", action=EnvDefault,
                        envvar='NEXUS_HOST')
    parser.add_argument("-p", "--password",
                        help="password for user 'admin'",
                        default="admin123", action=EnvDefault,
                        envvar="NEXUS_ADMIN_PASSWORD")
    parser.add_argument("-c", "--credential_file",
                        help="file containing password for user 'admin'",
                        action=EnvDefault, envvar="NEXUS_CREDENTIAL_FILE",
                        required=False)
    parser.add_argument("-g", "--groovy_dir",
                        help="directory containing groovy scripts to upload",
                        default=GROOVY_SCRIPTS_DIR, action=EnvDefault,
                        envvar="NEXUS_GROOVY_DIR")
    parser.add_argument("--config",
                        help="yaml configuration file path",
                        action=EnvDefault, envvar="NEXUS_CONFIG_FILE")
    return parser.parse_args()


def main():
    args = parse_args()
    print("Starting")
    if not args.config:
        fatal("No config file specified")
    passwords = [args.password]
    if args.credential_file is not None:
        try:
            with open(args.credential_file, "r") as credfile:
                for cred in credfile:
                    passwords.append(cred.strip())
        except FileNotFoundError:
            print("No credential file found at {}. Ignoring".format(args.credential_file))  # noqa
    nx = nexus_client(host=args.host, password_list=passwords)
    if not nx:
        fatal("No valid Nexus client")
    scripts_glob_path = os.path.join(args.groovy_dir, "*.groovy")
    scripts = glob.glob(scripts_glob_path)
    if len(scripts) == 0:
        fatal("No groovy scripts found at {}".format(scripts_glob_path))
    for script in scripts:
        print("Uploading {} to Nexus".format(script))
        nx.create_script(script)
    try:
        with open(args.config, "r") as configfile:
            config = process_config(configfile, os.environ)
    except FileNotFoundError:
        fatal("No config file found at {}".format(args.config))
    except yaml.YAMLError:
        fatal("Failure to parse yaml file found at {}".format(args.config))
    for config_step in config:
        for script_type, resources in config_step.items():
            for resource in resources:
                resp = nx.run_script(script_type, **resource)
                if len(resp.text) > 0 and 'result' in resp.json():
                    result = resp.json()['result']
                    print("{} result: {}".format(script_type, result))
                else:
                    print("{} result: {}".format(script_type, resp.text))


def process_config(file_handle, env=None):
    """
    Attempt to safe load a yaml file, rendering with jinja2.

    Pass in a file handle and a dictionary of environment variables
    to use as so:
        {{env['FOO']}}
    """
    env = env or None
    config = jinja2.Template(file_handle.read()).render(env=env)
    return yaml.safe_load(config)


def nexus_client(host, user=ADMIN_USER, password_list=None):
    """
    Return a preconfigured nexus client trying a list of passwords
    for the specified user

    Connections are attempted 10 times with increasing pauses.

    if None returned, all of the provided credentials were invalid.
    """
    password_list = password_list or []
    for password in password_list:
        try:
            return Nexus(host=host, user=user, password=password)
        except NexusUnauthorised:
            print("Credential attempted and was rejected")
        except NexusConnectionError:
            print("Connection attempted to {} but failed multiple times".format(host))  # noqa


def fatal(msg):
    print(msg)
    sys.exit(1)

if __name__ == "__main__":
    main()
