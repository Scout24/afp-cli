#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest2 import TestCase
from afp_cli.cli_functions import get_valid_seconds
from datetime import datetime
from mock import patch, Mock


class CliFunctionsTest(TestCase):

    def test_get_valid_seconds(self):
        future_date = '1970-01-01T00:30:00Z'
        utc_now = datetime(1970, 1, 1)
        self.assertEqual(get_valid_seconds(future_date, utc_now), 30*60)

    @patch('sys.stderr', Mock())
    def test_get_valid_seconds_catches(self):
        future_date = 'NO_SUCH_DATE'
        utc_now = datetime(1970, 1, 1)
        self.assertEqual(get_valid_seconds(future_date, utc_now), 3600)
