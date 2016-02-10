# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import json
import os
import subprocess
import sys
import tempfile

from .log import CMDLineExit, info

HUMAN = 'human'
JSON = 'json'
CSV = 'csv'
OUTPUT_FORMATS = [HUMAN, JSON, CSV]

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


def format_aws_credentials(credentials, prefix=''):
    """Format aws credentials with optional prefix"""
    return os.linesep.join(["{0}{1}='{2}'".format(prefix, key, value)
                            for (key, value) in sorted(credentials.items())])


def format_account_and_role_list(account_and_role_list, output_formt=HUMAN):
    if output_formt == HUMAN:
        padding = max([len(account) for account in account_and_role_list]) + 3
        return os.linesep.join(
            ["{0:<{2}} {1}".format(account, ",".join(sorted(roles)), padding)
             for account, roles in sorted(account_and_role_list.items())])
    elif output_formt == JSON:
        return json.dumps(account_and_role_list,
                          sort_keys=True,
                          indent=4,
                          separators=(',', ': '))
    elif output_formt == CSV:
        return (os.linesep.join([",".join([account] + roles) for account, roles
                                in sorted(account_and_role_list.items())]))
    else:
        raise CMDLineExit("'{0}' is not a valid output format.\n".
                          format(output_formt) +
                          "Valid options are: {0}".
                          format(OUTPUT_FORMATS))


def print_export(aws_credentials):
    if os.name == "nt":
        info(format_aws_credentials(aws_credentials, prefix='set '))
    else:
        info(format_aws_credentials(aws_credentials, prefix='export '))


def start_subshell(aws_credentials, account, role):
    info("Press CTRL+D to exit.")
    rc_script = tempfile.NamedTemporaryFile(mode='w')
    rc_script.write(RC_SCRIPT_TEMPLATE.format(role=role, account=account,
                                              valid_seconds=aws_credentials['AWS_VALID_SECONDS']))
    rc_script.write(format_aws_credentials(aws_credentials, prefix='export '))
    rc_script.flush()
    subprocess.call(
        ["bash", "--rcfile", rc_script.name],
        stdout=sys.stdout, stderr=sys.stderr, stdin=sys.stdin)
    info("Left AFP subshell.")


def start_subcmd(aws_credentials, account, role):
    batch_file = tempfile.NamedTemporaryFile(suffix=".bat", delete=False)
    batch_file.write(BATCH_FILE_TEMPLATE.format(role=role, account=account))
    batch_file.write(format_aws_credentials(aws_credentials, prefix='set '))
    batch_file.flush()
    batch_file.close()
    subprocess.call(
        ["cmd", "/K", batch_file.name])
    info("Left AFP subcmd.")
    os.unlink(batch_file.name)


def enter_subx(aws_credentials, account, role):
    info("Entering AFP subshell for account {0}, role {1}.".format(account, role))
    try:
        if os.name == "nt":
            start_subcmd(aws_credentials, account, role)
        else:
            start_subshell(aws_credentials, account, role)
    except Exception as exc:
        raise CMDLineExit("Failed to start subshell: %s" % exc)
