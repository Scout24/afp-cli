# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import getpass
from .log import info, debug, CMDLineExit

try:
    import keyring
except ImportError:  # pragma: no cover
    keyring = None

PROMPT = 'prompt'
KEYRING = 'keyring'
TESTING = 'testing'
PASSWORD_PROVIDERS = [PROMPT, KEYRING, TESTING]


def prompt_get_password(username):
    """Return password for the given user"""
    return getpass.getpass("Password for {0}: ".format(username))


def keyring_get_password(username):
    if keyring is None:
        raise CMDLineExit("You requested to use the 'keyring' module "
                          "as password provider, but do not have this "
                          "installed.")

    keyring_impl = keyring.get_keyring()
    if keyring_impl.__class__.__name__ == 'PlaintextKeyring':
        raise CMDLineExit("Aborting: the 'keyring' module has selected the "
                          "insecure 'PlaintextKeyring'.")

    debug("Note: will use the backend: '{0}'".format(keyring_impl))
    password = keyring.get_password('afp', username)
    if not password:
        info("No password found in keychain, please enter it now to store it.")
        password = prompt_get_password(username)
        keyring.set_password('afp', username, password)
    return password


def get_password(password_provider, username):
    if password_provider == PROMPT:
        password = prompt_get_password(username)
    elif password_provider == KEYRING:
        password = keyring_get_password(username)
    elif password_provider == TESTING:
        password = 'PASSWORD'
    else:
        raise CMDLineExit("'{0}' is not a valid password provider.\n".
                          format(password_provider) +
                          "Valid options are: {0}".
                          format(PASSWORD_PROVIDERS))

    return password
