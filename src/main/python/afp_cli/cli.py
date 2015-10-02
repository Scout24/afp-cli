"""
Command line client for the AFP (AWS Federation Proxy)

Usage:
    afp [--user=<username>] [--api-url=<api url>]
                              [--show | --export ] [(<accountname> [<rolename>])]

Options:
  -h --help                Show this.
  --user=<username>        The user you want to use.
  --api-url=<api url>      The URL of the AFP server.
  --show                   Show credentials instead of opening subshell.
  --export                 Show credentials in an export suitable format.
  <accountname>            The AWS account id you want to login to.
  <rolename>               The AWS role you want to use for login. Defaults to the first role.
"""

from __future__ import print_function, absolute_import, unicode_literals, division
import getpass
import os
import random
import socket
import subprocess
import sys
import tempfile
import yamlreader

from docopt import docopt
from datetime import datetime, timedelta
from afp_cli import AWSFederationClientCmd

CFGDIR = '/etc/afp-cli'


def error(message):
    print(message, file=sys.stderr)
    sys.exit(1)


def get_user(username):
    """Check if we have a given user, else take the current one"""
    return username or getpass.getuser()


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
    if ((SECONDS >= {AWS_VALID_SECONDS})) ; then
        echo EXPIRED
    else
        echo $((({AWS_VALID_SECONDS}-SECONDS)/60)) Min
    fi
}}

PS1="(AWS {account}/{role} \\$(afp_minutes_left)) $PS1"
export AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID}
export AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY}
export AWS_SESSION_TOKEN={AWS_SESSION_TOKEN}
export AWS_SECURITY_TOKEN={AWS_SECURITY_TOKEN}
"""

BATCH_FILE_TEMPLATE = """
@echo off
set PROMPT=$C AWS {account}/{role} $F

set AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID}
set AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY}
set AWS_SESSION_TOKEN={AWS_SESSION_TOKEN}
set AWS_SECURITY_TOKEN={AWS_SECURITY_TOKEN}
"""


def start_subshell(aws_credentials, role, account):
    print("Press CTRL+D to exit.")
    rc_script = tempfile.NamedTemporaryFile()
    rc_script.write(RC_SCRIPT_TEMPLATE.format(role=role, account=account, **aws_credentials))
    rc_script.flush()
    subprocess.call(
        ["bash", "--rcfile", rc_script.name],
        stdout=sys.stdout, stderr=sys.stderr, stdin=sys.stdin)
    print("Left AFP subshell.")


def start_subcmd(aws_credentials, role, account):
    batch_file = tempfile.NamedTemporaryFile(suffix=".bat", delete=False)
    batch_file.write(BATCH_FILE_TEMPLATE.format(role=role, account=account, **aws_credentials))
    batch_file.flush()
    batch_file.close()
    subprocess.call(
        ["cmd", "/K", batch_file.name])
    print("Left AFP subcmd.")
    os.unlink(batch_file.name)


def get_role(arguments, federation_client, account):
    if arguments['<rolename>']:
        return arguments['<rolename>']
    else:
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

    try:
        credentials_valid_until = datetime.strptime(
            aws_credentials['AWS_EXPIRATION_DATE'],
            "%Y-%m-%dT%H:%M:%SZ",)
    except Exception:
        default_seconds = 3600
        msg = ("Failed to parse expiration date '{0}' for "
               "AWS credentials, assuming {1} seconds.").format(
            aws_credentials['AWS_EXPIRATION_DATE'], default_seconds)
        print(msg, file=sys.stderr)
        credentials_valid_until = (datetime.utcnow() +
                                   timedelta(seconds=default_seconds))
    valid_seconds = (credentials_valid_until - datetime.utcnow()).seconds
    aws_credentials['AWS_VALID_SECONDS'] = valid_seconds
    return aws_credentials


def main():
    """Main function for script execution"""
    arguments = docopt(__doc__)
    try:
        config = load_config()
    except Exception as exc:
        error("Failed to load configuration: %s" % exc)

    api_url = arguments['--api-url'] or config.get('api_url')
    if api_url is None:
        api_url = 'https://{fqdn}/afp-api/latest'.format(fqdn=get_default_afp_server())
    username = get_user(arguments['--user'] or config.get("user"))
    password = get_password(username)
    federation_client = AWSFederationClientCmd(api_url=api_url,
                                               username=username,
                                               password=password)
    if arguments['<accountname>']:
        account = arguments['<accountname>']
        role = get_role(arguments, federation_client, account)
        aws_credentials = get_aws_credentials(federation_client, account, role)

        if arguments['--show']:
            for key, value in aws_credentials.items():
                print("{key}='{value}'".format(key=key, value=value))

        elif arguments['--export']:
            for key, value in aws_credentials.items():
                if os.name is "nt":
                    print("set {key}='{value}'".format(key=key, value=value))
                else:
                    print("export {key}='{value}'".format(key=key, value=value))

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
            federation_client.print_account_and_role_list()
        except Exception as exc:
            error("Failed to get account list from AWS: %s" % exc)
