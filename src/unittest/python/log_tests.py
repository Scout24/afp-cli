#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest2 import TestCase
from mock import patch

from afp_cli.log import error, debug


class LogTest(TestCase):

    @patch('sys.exit')
    def test_error(self, exit_mock):
        error('ERROR')
        exit_mock.assert_called_once_with(1)

    @patch('afp_cli.log.DEBUG', True)
    def test_debug(self):
        debug('DEBUG')
