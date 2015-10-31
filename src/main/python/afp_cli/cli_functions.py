from __future__ import print_function

import os
import sys
from datetime import datetime


def get_valid_seconds(aws_expiration_date, utcnow=datetime.utcnow()):
    try:
        credentials_valid_until = datetime.strptime(aws_expiration_date, "%Y-%m-%dT%H:%M:%SZ", )
        return (credentials_valid_until - utcnow).seconds
    except Exception:
        default_seconds = 3600
        msg = "Failed to parse expiration date '{0}' for AWS credentials, assuming {1} seconds.".format(
            aws_expiration_date, default_seconds)
        print(msg, file=sys.stderr)
        return default_seconds


def format_aws_credentials(credentials, prefix=''):
    """Format aws credentials with optional prefix"""
    return os.linesep.join(["{0}{1}='{2}'".format(prefix, key, value)
                            for (key, value) in sorted(credentials.items())])


def format_account_and_role_list(account_and_role_list):
    return os.linesep.join(["{0:<20} {1}".format(account, ",".join(sorted(roles)))
                            for account, roles in sorted(account_and_role_list.items())])
