#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command line client for the AFP (AWS Federation Proxy)

Usage:
    afp [--debug] [--user=<username>] [--password-provider=<provider>] [--api-url=<api-url>] [--server <servername>]
                              [--show | --export | --write [--profile=<profile_name>]] [(<accountname> [<rolename>])]

Options:
  -h --help                       Show this.
  -v --version                    Show version and exit.
  --debug                         Activate debug output.
  --user=<username>               The user you want to use.
  --server <servername>           The AFP server to use.
  --api-url=<api-url>             The URL of the AFP server (e.g. https://afp/afp-api/latest). Takes precedence over --server.
  --show                          Show credentials instead of opening subshell.
  --export                        Show credentials in an export suitable format.
  --write                         Write credentials to aws credentials file.
  --profile=<profile_name>        Which profile to use in the aws credentials file.
  --password-provider=<provider>  Password provider.
  <accountname>                   The AWS account id you want to login to.
  <rolename>                      The AWS role you want to use for login. Defaults to the first role.
"""  # NOQA, docopt stuff is allowed to be longcat, and longcat is loooong

from __future__ import absolute_import, division, print_function

import getpass

from docopt import docopt

from . import __version__, log
from .aws_credentials_file import write
from .cli_functions import (get_api_url,
                            get_aws_credentials,
                            get_first_role,
                            sanitize_credentials)
from .client import AWSFederationClientCmd
from .config import load_config
from .exporters import (enter_subx,
                        format_account_and_role_list,
                        format_aws_credentials,
                        print_export)
from .log import CMDLineExit, debug, error, info
from .password_providers import get_password


def main():

    try:
        unprotected_main()
    except CMDLineExit as e:
        error(e)


def unprotected_main():
    """Main function for script execution"""
    arguments = docopt(
        __doc__, version='afp-cli version {0}'.format(__version__))
    if arguments['--debug']:
        log.DEBUG = True
    debug(arguments)

    try:
        config = load_config()
    except Exception as exc:
        error("Failed to load configuration: %s" % exc)

    api_url = get_api_url(arguments, config)
    username = arguments['--user'] or config.get("user") or getpass.getuser()
    password_provider = (arguments['--password-provider'] or
                         config.get("password-provider") or
                         'prompt')

    password = get_password(password_provider, username)

    # Do the sanitize dance
    sanitize_credentials(username, password)

    federation_client = AWSFederationClientCmd(
        api_url=api_url, username=username, password=password)
    if arguments['<accountname>']:
        account = arguments['<accountname>']
        role = arguments['<rolename>'] or get_first_role(
            federation_client, account)
        aws_credentials = get_aws_credentials(federation_client, account, role)

        if arguments['--show']:
            info(format_aws_credentials(aws_credentials))
        elif arguments['--export']:
            print_export(aws_credentials)
        elif arguments['--write']:
            write(aws_credentials, profile_name=arguments['--profile'])
        else:
            enter_subx(aws_credentials, account, role)
    else:
        try:
            info(format_account_and_role_list(
                federation_client.get_account_and_role_list()))
        except Exception as exc:
            error("Failed to get account list from AWS: %s" % exc)
