from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import socket
import sys
from datetime import datetime

from .client import APICallError
from .log import CMDLineExit


def get_valid_seconds(aws_expiration_date, utcnow):
    try:
        credentials_valid_until = datetime.strptime(
            aws_expiration_date, "%Y-%m-%dT%H:%M:%SZ")
        return (credentials_valid_until - utcnow).seconds
    except ValueError:
        default_seconds = 3600
        msg = (
            "Failed to parse expiration date '{0}' for AWS credentials, "
            "assuming {1} seconds.").format(
            aws_expiration_date, default_seconds)
        print(msg, file=sys.stderr)
        return default_seconds


def sanitize_host(server_name):
    """
    Return the FQDN of the host passed.

    This is done by resolving the given server name into (potentially
    multiple) IPs. One of those IPs is randomly chosen, then a
    reverse-lookup is performed on that IP to get its FQDN.

    This effort is required to avoid certificate warnings about host
    name mismatch between the certificate and the hostname.

    This can also break if the admin of the server uses several IP
    addresses that do *not* resolve to a hostname mentioned in the
    TLS certificate.
    """
    try:
        addrinfo_tuple = socket.getaddrinfo(
            server_name, 443, socket.AF_INET, socket.SOCK_STREAM)
    except Exception as exc:
        raise CMDLineExit("Could not resolve hostname %r: %s" % (
            server_name, exc))
    # Take the first result, round-robin responses are default per DNS
    addrinfo = addrinfo_tuple[0]
    afp_server_ip = addrinfo[4][0]

    try:
        return socket.gethostbyaddr(afp_server_ip)[0]
    except Exception as exc:
        raise CMDLineExit("DNS reverse lookup failed for IP %s: %s" % (
            afp_server_ip, exc))


def get_api_url(arguments=None, config=None):
    """
    Return a calculated/sanitized API URL from config and/or command
    line parameters.
    """
    arguments = arguments or {}
    config = config or {}
    passed_api_url = arguments.get('--api-url') or config.get('api_url')
    if passed_api_url is not None:
        # No checks whatsoever, just return the preferred API URL
        return passed_api_url
    server_name = arguments.get('--server') or config.get('server') or 'afp'
    sanitized_server_name = sanitize_host(server_name)
    return 'https://{fqdn}/afp-api/latest'.format(fqdn=sanitized_server_name)


def get_first_role(federation_client, account):
    try:
        accounts_and_roles = federation_client.get_account_and_role_list()
        return sorted(accounts_and_roles[account])[0]
    except APICallError as exc:
        raise CMDLineExit("Failed to get account list from AWS: %s" % exc)
    except KeyError:
        raise CMDLineExit("%s is not a valid AWS account" % account)
    except IndexError:
        raise CMDLineExit("Could not find any role for account %s" % account)


def get_aws_credentials(federation_client, account, role):
    try:
        aws_credentials = federation_client.get_aws_credentials(account, role)
    except APICallError as exc:
        raise CMDLineExit("Failed to get credentials from AWS: %s" % repr(exc))
    else:
        aws_credentials['AWS_VALID_SECONDS'] = get_valid_seconds(
            aws_credentials['AWS_EXPIRATION_DATE'], datetime.utcnow())
        aws_credentials['AWS_ACCOUNT_NAME'] = account
        aws_credentials['AWS_ASSUMED_ROLE'] = role
        return aws_credentials


def sanitize_credentials(username, password):
    """
    Check if username and password contain non-ASCII characters,
    raise an exception when yes.

    Per convention, non-ASCII characters are not allowed in usernames
    and passwords. The reasoning is, afp-cli uses HTTP Authentication
    headers which does not go well with UTF-8 encoding.

    For details, see http://stackoverflow.com/a/703341
    """
    try:
        username.encode('ascii')
        password.encode('ascii')
    except (UnicodeDecodeError, UnicodeEncodeError):
        # PY3 UnicodeEncodeError, PY2 UnicodeDecodeError
        raise CMDLineExit(
            'Non-ASCII characters in username & password aren\'t allowed. '
            'See http://stackoverflow.com/a/703341')
