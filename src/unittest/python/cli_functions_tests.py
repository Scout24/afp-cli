#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest2 import TestCase
from datetime import datetime
from mock import patch, Mock

from afp_cli.cli_functions import (get_valid_seconds,
                                   get_first_role,
                                   get_aws_credentials,
                                   )
from afp_cli.client import APICallError
from afp_cli.log import CMDLineExit


class GetValidSecondsTest(TestCase):

    def test_get_valid_seconds(self):
        future_date = '1970-01-01T00:30:00Z'
        utc_now = datetime(1970, 1, 1)
        self.assertEqual(get_valid_seconds(future_date, utc_now), 30*60)

    @patch('sys.stderr', Mock())
    def test_get_valid_seconds_catches(self):
        future_date = 'NO_SUCH_DATE'
        utc_now = datetime(1970, 1, 1)
        self.assertEqual(get_valid_seconds(future_date, utc_now), 3600)


class GetFirstRoleTests(TestCase):

    def test_with_single_account_and_single_role(self):
        client = Mock()
        client.get_account_and_role_list.return_value = \
            {'ACCOUNT1': ['ROLE1']}
        self.assertEqual('ROLE1', get_first_role(client, 'ACCOUNT1'))

    def test_with_single_account_and_multiple_roles(self):
        client = Mock()
        client.get_account_and_role_list.return_value = \
            {'ACCOUNT1': ['ROLE1', 'ROLE2']}
        self.assertEqual('ROLE1', get_first_role(client, 'ACCOUNT1'))

    def test_with_multiple_accounts_and_multiple_roles(self):
        client = Mock()
        client.get_account_and_role_list.return_value = \
            {'ACCOUNT1': ['ROLE1', 'ROLE2'],
             'ACCOUNT2': ['ROLE3', 'ROLE4']}
        self.assertEqual('ROLE1', get_first_role(client, 'ACCOUNT1'))

    def test_excpetion_when_fetching_roles(self):
        client = Mock()
        client.get_account_and_role_list.side_effect = APICallError
        self.assertRaises(CMDLineExit, get_first_role, client, 'ANY_ACCOUNT')

    def test_excpetion_when_looking_for_account(self):
        client = Mock()
        client.get_account_and_role_list.return_value = \
            {'ACCOUNT1': ['ROLE1']}
        self.assertRaises(CMDLineExit, get_first_role, client, 'ACCOUNT2')

    def test_excpetion_when_looking_for_role(self):
        client = Mock()
        client.get_account_and_role_list.return_value = \
            {'ACCOUNT1': []}
        self.assertRaises(CMDLineExit, get_first_role, client, 'ACCOUNT1')


class GetAWSCredentialsTest(TestCase):

    @patch('afp_cli.cli_functions.get_valid_seconds', Mock(return_value=600))
    def test_getting_valid_aws_credentials(self):
        client = Mock()
        client.get_aws_credentials.return_value = \
            {'AWS_CREDENTIALS': 'SECRET',
             'AWS_EXPIRATION_DATE': 'DATE'}
        expected = {
            'AWS_CREDENTIALS': 'SECRET',
            'AWS_VALID_SECONDS': 600,
            'AWS_ACCOUNT_NAME': 'ACCOUNT1',
            'AWS_ASSUMED_ROLE': 'ROLE1',
            'AWS_EXPIRATION_DATE': 'DATE',
        }
        received = get_aws_credentials(client, 'ACCOUNT1', 'ROLE1')
        self.assertEqual(expected, received)

    def test_excpetion(self):
        client = Mock()
        client.get_aws_credentials.side_effect = APICallError
        self.assertRaises(CMDLineExit, get_aws_credentials, client, 'ACCOUNT1', 'ROLE1')
