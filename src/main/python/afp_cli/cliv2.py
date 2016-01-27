# -*- coding: utf-8 -*-
"""
Command line client for the AFP V2 (AWS Federation Proxy)

Usage:
    afp [options] help
    afp [options] version
    afp [options] list
    afp [options] (show | export | write | subshell) <accountname> [<rolename>]

Options:
  -h, --help                          Show this.
  -d, --debug                         Activate debug output.
  -u, --user <username>               The user you want to use.
  -s, --server <servername>           The AFP server to use.
  -a, --api-url <api-url>             The URL of the AFP server (e.g. https://afp/afp-api/latest). Takes precedence over --server.
  -p, --password-provider <provider>  Password provider. Valid values are: 'prompt', 'keyring' and 'testing'.
  <accountname>                       The AWS account id you want to login to.
  <rolename>                          The AWS role you want to use for login. Defaults to the first role.

Subcommands:
  help                                Show help.
  version                             Show version.
  list                                List available accounts and roles.
  show                                Show credentials.
  export                              Show credentials in an export suitable format.
  write                               Write credentials to aws credentials file.
  subshell                            Open a subshell with exported credentials.
"""  # NOQA, docopt stuff is allowed to be longcat, and longcat is loooong

from __future__ import absolute_import, division, print_function

import getpass

from docopt import docopt

from . import log
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

HELP, VERSION, LIST, SHOW, EXPORT, WRITE, SUBSHELL = \
    'help', 'version', 'list', 'show', 'export', 'write', 'subshell'

SUBCOMMANDS = [HELP, VERSION, LIST, SHOW, EXPORT, WRITE, SUBSHELL]
ASSUME_SUBCOMMANDS = [SHOW, EXPORT, WRITE, SUBSHELL]


def main():
    try:
        unprotected_main()
    except CMDLineExit as e:
        error(e)


def unprotected_main():
    """Main function for script execution"""
    arguments = docopt(__doc__)
    if arguments['--debug']:
        log.DEBUG = True
    debug(arguments)

    # parse the subcommand, only one will be active
    subcommand = [s for s in SUBCOMMANDS if arguments[s]][0]
    debug("Subcommand is '{0}'".format(subcommand))

    if subcommand == VERSION:
        info('Reporting version is not implemented yet')
        return 0
    elif subcommand == HELP:
        # exit early with help message
        docopt(__doc__, argv=['--help'])

    try:
        config = load_config()
    except Exception as exc:
        error("Failed to load configuration: %s" % exc)

    api_url = get_api_url(arguments, config)
    debug("'api-url' is '{0}'".format(api_url))
    username = arguments['--user'] or config.get("user") or getpass.getuser()
    debug("'username' is '{0}'".format(username))
    password_provider = (arguments['--password-provider'] or
                         config.get("password-provider") or
                         'prompt')
    debug("'password-provider' is '{0}'".format(password_provider))

    password = get_password(password_provider, username)

    # Do the sanitize dance
    sanitize_credentials(username, password)

    federation_client = AWSFederationClientCmd(
        api_url=api_url, username=username, password=password)

    aws_credentials = None
    if subcommand in ASSUME_SUBCOMMANDS:
        account = arguments['<accountname>']
        role = arguments.get('<rolename>') or \
            get_first_role(federation_client, account)
        aws_credentials = get_aws_credentials(federation_client, account, role)

    if arguments['list']:
        try:
            info(format_account_and_role_list(
                federation_client.get_account_and_role_list()))
        except Exception as exc:
            error("Failed to get account list from AWS: %s" % exc)
    elif arguments['show']:
        info(format_aws_credentials(aws_credentials))
    elif arguments['export']:
        print_export(aws_credentials)
    elif arguments['write']:
        write(aws_credentials)
    elif arguments['subshell']:
        enter_subx(aws_credentials, account, role)
