#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
from datetime import datetime

from afp_cli.cli_functions import (get_api_url,
                                   get_aws_credentials,
                                   get_first_role,
                                   get_valid_seconds,
                                   sanitize_credentials,
                                   sanitize_host)
from afp_cli.client import APICallError
from afp_cli.log import CMDLineExit
from mock import Mock, patch
from six import PY2, PY3
from unittest2 import TestCase, skipIf


class GetValidSecondsTest(TestCase):

    def test_get_valid_seconds(self):
        future_date = '1970-01-01T00:30:00Z'
        utc_now = datetime(1970, 1, 1)
        self.assertEqual(get_valid_seconds(future_date, utc_now), 30 * 60)

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
        self.assertRaises(
            CMDLineExit, get_aws_credentials, client, 'ACCOUNT1', 'ROLE1')


class SanitizeCredentialsTest(TestCase):

    @skipIf(PY3, 'Python 2 only')
    def test_py2_utf8(self):
        username = 'a'
        password = 'ö'
        with self.assertRaises(CMDLineExit):
            sanitize_credentials(username, password)

    @skipIf(PY2, 'Python 3 only')
    def test_py3_utf8(self):
        username = 'a'
        password = 'ö'
        with self.assertRaises(CMDLineExit):
            sanitize_credentials(username, password)


class GetApiUrlTest(TestCase):
    """
    Tests for get_api_url()
    """

    def setUp(self):
        self.patch_sanitize_host = patch('afp_cli.cli_functions.sanitize_host')
        self.mock_sanitize_host = self.patch_sanitize_host.start()
        self.mock_sanitize_host.return_value = 'FQDN'

    def tearDown(self):
        self.patch_sanitize_host.stop()

    def test_returns_passed_apiurl_over_everything(self):
        """
        When an apiurl is passed, return it without any preliminary
        check.
        """
        arguments = {'--api-url': 'passed_stuff'}
        config = {'api_url': 'irrelevant_stuff'}
        result = get_api_url(arguments, config)
        self.assertEqual(result, 'passed_stuff')
        self.mock_sanitize_host.assert_not_called()

    def test_returns_configured_apiurl_over_default(self):
        """
        When an apiurl is configured, returned it without any
        preliminary check.
        """
        arguments = {'--api-url': None}
        config = {'api_url': 'configured_stuff'}
        result = get_api_url(arguments, config)
        self.assertEqual(result, 'configured_stuff')
        self.mock_sanitize_host.assert_not_called()

    def test_uses_servername_parameter_when_no_apiurl_defined(self):
        """
        When servername is passed as a parameter, return it after
        running `sanitize_host` on it.
        """
        arguments = {
            '--api-url': None,
            '--server': 'passed_stuff'}
        config = {
            'api_url': None,
            'server': None}
        result = get_api_url(arguments, config)
        self.assertEqual(result, 'https://FQDN/afp-api/latest')
        self.mock_sanitize_host.assert_called_once_with('passed_stuff')

    def test_uses_configured_servername_when_no_apiurl_defined(self):
        """
        When servername is configured in the config, returned it after
        running `sanitize_host` on it.
        """
        arguments = {
            '--api-url': None,
            '--server': None}
        config = {
            'api_url': None,
            'server': 'configured_stuff'}
        result = get_api_url(arguments, config)
        self.assertEqual(result, 'https://FQDN/afp-api/latest')
        self.mock_sanitize_host.assert_called_once_with('configured_stuff')

    def test_defaults_to_afp_url_when_nothing_defined(self):
        """
        When nothing is configured/passed, return the default afp URL
        after running `sanitize_host` on it.
        """
        arguments = {
            '--api-url': None,
            '--server': None}
        config = {
            'api_url': None,
            'server': None}
        result = get_api_url(arguments, config)
        self.assertEqual(result, 'https://FQDN/afp-api/latest')
        self.mock_sanitize_host.assert_called_once_with('afp')


class SanitizeHostTest(TestCase):
    """
    Test cases for `sanitize_host()`.
    """

    def setUp(self):
        self.patch_getaddrinfo = patch('socket.getaddrinfo')
        self.mock_getaddrinfo = self.patch_getaddrinfo.start()
        self.patch_gethostbyaddr = patch('socket.gethostbyaddr')
        self.mock_gethostbyaddr = self.patch_gethostbyaddr.start()

    def tearDown(self):
        self.patch_getaddrinfo.stop()
        self.patch_gethostbyaddr.stop()

    def test_raises_error_on_hostnotfound(self):
        """
        Raise an error when the host is not resolvable.
        """
        self.mock_getaddrinfo.side_effect = socket.gaierror('error_message')
        return_value = None
        with self.assertRaises(CMDLineExit) as cm:
            return_value = sanitize_host('erroneous_host')
        self.assertIsNone(return_value)
        self.assertEqual(
            cm.exception.args[0],
            'Could not resolve hostname \'afp\': error_message')
        self.mock_getaddrinfo.assert_called_once_with(
            'erroneous_host', 443, socket.AF_INET, socket.SOCK_STREAM)
        self.mock_gethostbyaddr.assert_not_called()

    def test_raises_error_on_reversenotfound(self):
        """
        Raise an error when the host is resolvable, but it's reverse is
        not.
        """
        self.mock_getaddrinfo.return_value = (
            [0, 1, 2, 3, ['take_me', 'not_me']],)
        self.mock_gethostbyaddr.side_effect = socket.gaierror('error_message')
        return_value = None
        with self.assertRaises(CMDLineExit) as cm:
            return_value = sanitize_host('erroneous_host')
        self.assertIsNone(return_value)
        self.assertEqual(
            cm.exception.args[0],
            'DNS reverse lookup failed for IP take_me: error_message')
        self.mock_getaddrinfo.assert_called_once_with(
            'erroneous_host', 443, socket.AF_INET, socket.SOCK_STREAM)
        self.mock_gethostbyaddr.assert_called_once_with('take_me')

    def test_returns_proper_fqdn(self):
        """
        Return the proper FQDN of the host when it's resolvable both
        ways.
        """
        self.mock_getaddrinfo.return_value = (
            [0, 1, 2, 3, ['take_me', 'not_me']],)
        self.mock_gethostbyaddr.return_value = ['proper_FQDN']
        return_value = sanitize_host('erroneous_host')
        self.mock_getaddrinfo.assert_called_once_with(
            'erroneous_host', 443, socket.AF_INET, socket.SOCK_STREAM)
        self.mock_gethostbyaddr.assert_called_once_with('take_me')
        self.assertEqual(return_value, 'proper_FQDN')
