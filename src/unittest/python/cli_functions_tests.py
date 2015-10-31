#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest2 import TestCase
from afp_cli import cli
from datetime import datetime


class CliFunctionsTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

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
        self.assertEqual(cli.get_valid_seconds('2016-08-16T07:45:00Z', datetime(2016, 8, 16, hour=7, minute=15)),
                         30*60)

    def test_format_account_and_one_role(self):
        self.assertEqual(cli.format_account_and_role_list({"testaccount1": ["testrole1"]}),
                         "testaccount1         testrole1")

    def test_format_account_and_two_roles(self):
        self.assertEqual(cli.format_account_and_role_list({"testaccount2": ["testrole1", "testrole2"]}),
                         "testaccount2         testrole1,testrole2")
