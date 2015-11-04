#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest2 import TestCase
import afp_cli.cli_functions as cli
from datetime import datetime


class CliFunctionsTest(TestCase):

    def test_format_aws_credentials_with_prefix(self):
        credentials = {"AWS_ACCESS_KEY_ID": "testAccessKey"}
        self.assertEqual(cli.format_aws_credentials(credentials),
                         "AWS_ACCESS_KEY_ID='testAccessKey'")

        self.assertEqual(cli.format_aws_credentials(credentials, prefix='export '),
                         "export AWS_ACCESS_KEY_ID='testAccessKey'")

        self.assertEqual(cli.format_aws_credentials(credentials, prefix='set '),
                         "set AWS_ACCESS_KEY_ID='testAccessKey'")

    def test_format_aws_credentials_multline(self):
        input_ = {"AWS_ACCESS_KEY_ID": "testAccessKey",
                  "AWS_SECRET_ACCESS_KEY": "not so secret"}

        self.assertEqual(cli.format_aws_credentials(input_),
                         "AWS_ACCESS_KEY_ID='testAccessKey'\nAWS_SECRET_ACCESS_KEY='not so secret'")

    def test_get_valid_seconds(self):
        future_date = '1970-01-01T00:30:00Z'
        utc_now = datetime(1970, 1, 1)
        self.assertEqual(cli.get_valid_seconds(future_date, utc_now), 30*60)

    def test_get_valid_seconds_catches(self):
        future_date = 'NO_SUCH_DATE'
        utc_now = datetime(1970, 1, 1)
        self.assertEqual(cli.get_valid_seconds(future_date, utc_now), 3600)

    def test_format_account_and_one_role(self):
        self.assertEqual(cli.format_account_and_role_list({"testaccount1": ["testrole1"]}),
                         "testaccount1         testrole1")

    def test_format_account_and_two_roles(self):
        self.assertEqual(cli.format_account_and_role_list({"testaccount2": ["testrole1", "testrole2"]}),
                         "testaccount2         testrole1,testrole2")
