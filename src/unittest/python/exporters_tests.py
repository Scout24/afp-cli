#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest2 import TestCase
from afp_cli.exporters import (format_aws_credentials,
                               format_account_and_role_list,
                               )


class FormattingTest(TestCase):

    def test_format_aws_credentials_with_prefix(self):
        credentials = {"AWS_ACCESS_KEY_ID": "testAccessKey"}
        self.assertEqual(format_aws_credentials(credentials),
                         "AWS_ACCESS_KEY_ID='testAccessKey'")

        self.assertEqual(format_aws_credentials(credentials, prefix='export '),
                         "export AWS_ACCESS_KEY_ID='testAccessKey'")

        self.assertEqual(format_aws_credentials(credentials, prefix='set '),
                         "set AWS_ACCESS_KEY_ID='testAccessKey'")

    def test_format_aws_credentials_multline(self):
        input_ = {"AWS_ACCESS_KEY_ID": "testAccessKey",
                  "AWS_SECRET_ACCESS_KEY": "not so secret"}

        self.assertEqual(format_aws_credentials(input_),
                         "AWS_ACCESS_KEY_ID='testAccessKey'\nAWS_SECRET_ACCESS_KEY='not so secret'")

    def test_format_account_and_one_role(self):
        self.assertEqual(format_account_and_role_list({"testaccount1": ["testrole1"]}),
                         "testaccount1         testrole1")

    def test_format_account_and_two_roles(self):
        self.assertEqual(format_account_and_role_list({"testaccount2": ["testrole1", "testrole2"]}),
                         "testaccount2         testrole1,testrole2")
