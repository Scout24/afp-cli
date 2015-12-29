#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest2 import TestCase

from mock import patch, Mock

from afp_cli.password_providers import (prompt_get_password,
                                        keyring_get_password,
                                        get_password,
                                        PROMPT,
                                        KEYRING,
                                        TESTING,
                                        )
from afp_cli.log import CMDLineExit


class TestPromptGetPassWord(TestCase):

    @patch('getpass.getpass')
    def test_getapss_called(self, getpass_mock):
        expected = 'PASSWORD'
        getpass_mock.return_value = expected
        received = prompt_get_password('USERNAME')
        self.assertEqual(expected, received)
        getpass_mock.assert_called_once_with('Password for USERNAME: ')


class TestKeyringGetPassword(TestCase):

    @patch('afp_cli.password_providers.keyring', None)
    def test_import_fails_on_no_keyring_module(self):
        self.assertRaises(CMDLineExit, keyring_get_password, 'USERNAME')

    @patch('afp_cli.password_providers.keyring')
    def test_abort_in_case_of_plaintext_backend(self, keyring_mock):
        keyring_mock.get_keyring.return_value.__class__.__name__ = \
            'PlaintextKeyring'
        self.assertRaises(CMDLineExit, keyring_get_password, 'USERNAME')

    @patch('afp_cli.password_providers.keyring')
    def test_retrieve_password_if_exists(self, keyring_mock):
        expected = 'PASSWORD'
        keyring_mock.get_password = Mock(return_value=expected)
        received = keyring_get_password('USERNAME')
        self.assertEqual(expected, received)
        keyring_mock.get_password.assert_called_once_with('afp', 'USERNAME')

    @patch('afp_cli.password_providers.keyring')
    @patch('afp_cli.password_providers.prompt_get_password')
    def test_prompt_and_store_password_if_it_doesnt_exists(self,
                                                           prompt_mock,
                                                           keyring_mock):
        expected = 'PASSWORD'
        username = 'USERNAME'
        prompt_mock.return_value = expected
        keyring_mock.get_password.return_value = None
        received = keyring_get_password('USERNAME')
        self.assertEqual(expected, received)
        keyring_mock.get_password.assert_called_once_with('afp', username)
        keyring_mock.set_password.assert_called_once_with('afp',
                                                          username, expected)


class TestGetPassword(TestCase):

    @patch('afp_cli.password_providers.prompt_get_password',
           Mock(return_value='PASSWORD'))
    def test_prompt(self):
        self.assertEqual('PASSWORD', get_password(PROMPT, 'USERNAME'))

    @patch('afp_cli.password_providers.keyring_get_password',
           Mock(return_value='PASSWORD'))
    def test_keyring(self):
        self.assertEqual('PASSWORD', get_password(KEYRING, 'USERNAME'))

    def test_testing(self):
        self.assertEqual('PASSWORD', get_password(TESTING, 'USERNAME'))

    def test_fail(self):
        self.assertRaises(CMDLineExit, get_password,
                          'NOSUCHPROVIDER', 'USERNAME')
