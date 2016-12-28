# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division

import os

import yamlreader


CFGDIR = '/etc/afp-cli'


def load_config(global_config_dir=CFGDIR):
    global_config = {}
    if os.path.isdir(global_config_dir):
        global_config = yamlreader.yaml_load(global_config_dir, {})

    user_config = {}
    user_config_dir = os.path.expanduser("~/.afp-cli")
    if os.path.isdir(user_config_dir):
        user_config = yamlreader.yaml_load(user_config_dir, {})

    yamlreader.data_merge(global_config, user_config)
    return global_config
