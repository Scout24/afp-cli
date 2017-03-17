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

    # For older 'keyring' module (<8.0) implementation where undesirable
    # implementations were still permissable. And, for newer ones (>=8.0),
    # where the 'fail' module is used to denote no available keyrings.
    undesirable = ['keyring.backends.file.PlaintextKeyring',  # <  8.0
                   'keyring.backends.file.EncryptedKeyring',  # <  8.0
                   'keyrings.alt.file.EncryptedKeyring',      # >= 8.0
                   'keyring.backends.fail.Keyring',           # >= 8.0
                   ]
    # TODO: there has got to be a better way
    description = '.'.join((keyring_impl.__class__.__module__,
                            keyring_impl.__class__.__name__))
    debug("Description of the backend is: '{0}'".format(description))
    if description in undesirable:
        msg = ("Aborting: Did not find a usable backend to access your "
               "keyring.\n\n"
               "Maybe 'pip install keyrings.alt' will fix your problem.")
        raise CMDLineExit(msg)

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
