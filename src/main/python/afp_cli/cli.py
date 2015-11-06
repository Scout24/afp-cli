"""
Command line client for the AFP (AWS Federation Proxy)

Usage:
    afp [--debug] [--user=<username>] [--no-ask-pw] [--api-url=<api-url>]
                              [--show | --export | --write] [(<accountname> [<rolename>])]

Options:
  -h --help                Show this.
  --debug                  Activate debug output.
  --user=<username>        The user you want to use.
  --api-url=<api-url>      The URL of the AFP server (e.g. https://afp/afp-api/latest).
  --show                   Show credentials instead of opening subshell.
  --export                 Show credentials in an export suitable format.
  --write                  Write credentials to aws credentials file.
  --no-ask-pw              Don't prompt for password (for testing only).
  <accountname>            The AWS account id you want to login to.
  <rolename>               The AWS role you want to use for login. Defaults to the first role.
"""

from __future__ import print_function, absolute_import, division
from datetime import datetime
import getpass
import os
import random
import socket
import subprocess
import sys
import tempfile
import yamlreader

from docopt import docopt
from afp_cli import AWSFederationClientCmd, aws_credentials_file
import afp_cli.cli_functions as cli

CFGDIR = '/etc/afp-cli'
DEBUG = False


def error(message):
    print(message, file=sys.stderr)
    sys.exit(1)


def debug(message):
    if DEBUG:
        print(message)


def get_password(username):
    """Return password for the given user"""
    return getpass.getpass(b"Password for {0}: ".format(username))


def load_config(global_config_dir=CFGDIR):
    global_config = {}
    if os.path.isdir(global_config_dir):
        global_config = yamlreader.yaml_load(global_config_dir, {})

    user_config = {}
    user_config_dir = os.path.expanduser("~/.afp-cli")
    if os.path.isdir(user_config_dir):
        global_config = yamlreader.yaml_load(user_config_dir, {})

    yamlreader.data_merge(global_config, user_config)
    return global_config


def get_default_afp_server():
    """Return the FQDN of the host that is called "afp"

    This is done by resolving "afp" into (potentially multiple) IPs.
    One of those IPs is randomly chosen, then a reverse-lookup is performed
    on that IP to get its FQDN.
    """
    try:
        addrinfos = socket.getaddrinfo("afp", 443,
                                       socket.AF_INET, socket.SOCK_STREAM)
    except Exception as exc:
        error("Could not resolve hostname 'afp': %s" % exc)
    addrinfo = random.choice(addrinfos)
    afp_server_ip = addrinfo[4][0]

    try:
        return socket.gethostbyaddr(afp_server_ip)[0]
    except Exception as exc:
        error("DNS reverse lookup failed for IP %s: %s" % (
            afp_server_ip, exc))

RC_SCRIPT_TEMPLATE = """
# Pretend to be an interactive, non-login shell
for file in /etc/bash.bashrc ~/.bashrc; do
    [ -f "$file" ] && . "$file"
done

function afp_minutes_left {{
    if ((SECONDS >= {valid_seconds})) ; then
        echo EXPIRED
    else
        echo $((({valid_seconds}-SECONDS)/60)) Min
    fi
}}

PS1="(AWS {account}/{role} \\$(afp_minutes_left)) $PS1"
"""

BATCH_FILE_TEMPLATE = """
@echo off
set PROMPT=$C AWS {account}/{role} $F
"""


def start_subshell(aws_credentials, role, account):
    print("Press CTRL+D to exit.")
    rc_script = tempfile.NamedTemporaryFile(mode='w')
    rc_script.write(RC_SCRIPT_TEMPLATE.format(role=role, account=account,
                                              valid_seconds=aws_credentials['AWS_VALID_SECONDS']))
    rc_script.write(cli.format_aws_credentials(aws_credentials, prefix='export '))
    rc_script.flush()
    subprocess.call(
        ["bash", "--rcfile", rc_script.name],
        stdout=sys.stdout, stderr=sys.stderr, stdin=sys.stdin)
    print("Left AFP subshell.")


def start_subcmd(aws_credentials, role, account):
    batch_file = tempfile.NamedTemporaryFile(suffix=".bat", delete=False)
    batch_file.write(BATCH_FILE_TEMPLATE.format(role=role, account=account))
    batch_file.write(cli.format_aws_credentials(aws_credentials, prefix='set '))
    batch_file.flush()
    batch_file.close()
    subprocess.call(
        ["cmd", "/K", batch_file.name])
    print("Left AFP subcmd.")
    os.unlink(batch_file.name)


def get_first_role(federation_client, account):
    try:
        accounts_and_roles = federation_client.get_account_and_role_list()
    except Exception as exc:
        error("Failed to get account list from AWS: %s" % exc)

    try:
        return sorted(accounts_and_roles[account])[0]
    except KeyError:
        error("%s is not a valid AWS account" % account)
    except IndexError:
        error("Could not find any role for account %s" % account)


def get_aws_credentials(federation_client, account, role):
    try:
        aws_credentials = federation_client.get_aws_credentials(account, role)
    except Exception as exc:
        error("Failed to get credentials from AWS: %s" % exc)

    aws_credentials['AWS_VALID_SECONDS'] = cli.get_valid_seconds(aws_credentials['AWS_EXPIRATION_DATE'],
                                                                 datetime.utcnow())
    aws_credentials['AWS_ACCOUNT_NAME'] = account
    aws_credentials['AWS_ASSUMED_ROLE'] = role
    return aws_credentials


def main():
    """Main function for script execution"""
    arguments = docopt(__doc__)
    if arguments['--debug']:
        global DEBUG
        DEBUG = True
    debug(arguments)

    try:
        config = load_config()
    except Exception as exc:
        error("Failed to load configuration: %s" % exc)

    api_url = arguments['--api-url'] or config.get('api_url') or \
        'https://{fqdn}/afp-api/latest'.format(fqdn=get_default_afp_server())
    username = arguments['--user'] or config.get("user") or getpass.getuser()
    password = 'PASSWORD' if arguments['--no-ask-pw'] else get_password(username)
    federation_client = AWSFederationClientCmd(api_url=api_url,
                                               username=username,
                                               password=password)
    if arguments['<accountname>']:
        account = arguments['<accountname>']
        role = arguments['<rolename>'] or get_first_role(federation_client, account)
        aws_credentials = get_aws_credentials(federation_client, account, role)

        if arguments['--show']:
            print(cli.format_aws_credentials(aws_credentials))

        elif arguments['--export']:
            if os.name == "nt":
                print(cli.format_aws_credentials(aws_credentials, prefix='set '))
            else:
                print(cli.format_aws_credentials(aws_credentials, prefix='export '))
        elif arguments['--write']:
            aws_credentials_file.write(aws_credentials)
        else:
            print("Entering AFP subshell for account {0}, role {1}.".format(
                account, role))
            try:
                if os.name == "nt":
                    start_subcmd(aws_credentials=aws_credentials, role=role, account=account)
                else:
                    start_subshell(aws_credentials=aws_credentials, role=role, account=account)
            except Exception as exc:
                error("Failed to start subshell: %s" % exc)
    else:
        try:
            print(cli.format_account_and_role_list(federation_client.get_account_and_role_list()))
        except Exception as exc:
            error("Failed to get account list from AWS: %s" % exc)
