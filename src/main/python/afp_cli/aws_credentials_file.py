# -*- coding: utf-8 -*-
from six.moves import configparser
from afp_cli.compat import OrderedDict
import os
import six
from .log import info


def write(aws_credentials, filename=None, profile_name=None):
    profile_name = profile_name or 'default'

    if six.PY2:
        # WTF
        ORIG_DEFAULTSECT = configparser.DEFAULTSECT
        configparser.DEFAULTSECT = 'default'

    try:

        if not filename:
            filename = os.path.expanduser("~") + '/.aws/credentials'

        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        config = configparser.RawConfigParser(dict_type=OrderedDict)
        config.read(filename)

        if not config.has_section(profile_name) and \
                (profile_name.lower() != 'default' or six.PY3):
            config.add_section(profile_name)

        config.set(profile_name, 'aws_access_key_id',
                   aws_credentials['AWS_ACCESS_KEY_ID'])
        config.set(profile_name, 'aws_secret_access_key',
                   aws_credentials['AWS_SECRET_ACCESS_KEY'])
        config.set(profile_name, 'aws_session_token',
                   aws_credentials['AWS_SESSION_TOKEN'])
        config.set(profile_name, 'aws_security_token',
                   aws_credentials['AWS_SECURITY_TOKEN'])

        with open(filename, 'w') as config_file:
            config.write(config_file)
        info("Wrote credentials to file: '{0}'".format(filename))

    finally:
        if six.PY2:
            configparser.DEFAULTSECT = ORIG_DEFAULTSECT
