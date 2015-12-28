#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getpass
from .log import error, debug

PROMPT = 'prompt'
KEYRING = 'keyring'
TESTING = 'testing'
PASSWORD_PROVIDERS = [PROMPT, KEYRING, TESTING]


def prompt_get_password(username):
    """Return password for the given user"""
    return getpass.getpass(b"Password for {0}: ".format(username))


def keyring_get_password(username):

    try:
        import keyring
    except ImportError:
        error("You requested to use the 'keyring' module as password provider, "
              "but do not have this installed.")

    keyring_impl = keyring.get_keyring()
    if keyring_impl.__class__.__name__ == 'PlaintextKeyring':
        error("Aborting: the 'keyring' module has selected the insecure 'PlaintextKeyring'.")

    debug("Note: will use the backend: '{}'".format(keyring_impl))
    password = keyring.get_password('afp', username)
    if not password:
        print("No password found in keychain, please enter it now to store it.")
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
        error("'{0}' is not a valid password provider.\n".format(password_provider) +
              "Valid options are: {0}".format(str(PASSWORD_PROVIDERS)))

    return password
