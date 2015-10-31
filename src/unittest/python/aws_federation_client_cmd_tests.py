#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals, division

from mock import patch, Mock
from unittest2 import TestCase
from afp_cli import AWSFederationClientCmd


class AWSFederationClientCmdTest(TestCase):
    def setUp(self):
        self.api_client = AWSFederationClientCmd()

    @patch("afp_cli.client.requests.get")
    def test_get_correct_account_and_role_list(self, mock_get):
        expected_result = Mock(text='{"testaccount": ["testrole"]}',
                               status_code=200,
                               reason="Ok")
        mock_get.return_value = expected_result
        result = self.api_client.get_account_and_role_list()
        self.assertEqual(result, {"testaccount": ["testrole"]}, msg='Should be the same')

    @patch("afp_cli.client.requests.get")
    def test_get_correct_aws_credentials(self, mock_get):
        expected_result = Mock(text='{"Code": "Success", '
                                    '"AccessKeyId": "testAccessKey", '
                                    '"SecretAccessKey": "testSecretAccessKey", '
                                    '"Token": "testToken", '
                                    '"Expiration": "2015-01-01T12:34:56Z"}',
                               status_code=200,
                               reason="Ok")
        mock_get.return_value = expected_result
        result = self.api_client.get_aws_credentials("testaccount", "testrole")
        self.assertEqual(result, {"AWS_ACCESS_KEY_ID": "testAccessKey",
                                  "AWS_SECRET_ACCESS_KEY": "testSecretAccessKey",
                                  "AWS_SESSION_TOKEN": "testToken",
                                  "AWS_SECURITY_TOKEN": "testToken",
                                  "AWS_EXPIRATION_DATE": "2015-01-01T12:34:56Z"},
                         msg='Should be the same')

    @patch("six.moves.builtins.print")
    @patch("afp_cli.client.AWSFederationClientCmd.get_account_and_role_list")
    def test_print_account_and_one_role_with_correct_format(self, mock_get_account_and_role_list, mock_print):
        expected_result = {"testaccount1": ["testrole1"]}
        mock_get_account_and_role_list.return_value = expected_result
        self.api_client.print_account_and_role_list()
        mock_print.assert_called_with("testaccount1         testrole1")

    @patch("six.moves.builtins.print")
    @patch("afp_cli.client.AWSFederationClientCmd.get_account_and_role_list")
    def test_print_account_and_two_roles_with_correct_format(self, mock_get_account_and_role_list, mock_print):
        expected_result = {"testaccount2": ["testrole1", "testrole2"]}
        mock_get_account_and_role_list.return_value = expected_result
        self.api_client.print_account_and_role_list()
        mock_print.assert_called_with("testaccount2         testrole1,testrole2")
