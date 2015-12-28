#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from unittest2 import TestCase
from textwrap import dedent

from mock import patch, Mock

from six import StringIO

from afp_cli.exporters import (format_aws_credentials,
                               format_account_and_role_list,
                               print_export,
                               start_subshell,
                               start_subcmd,
                               enter_subx,
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

    @patch('os.name', 'unix')
    @patch('afp_cli.exporters.format_aws_credentials')
    def test_print_export_unix(self, format_mock):
        print_export('CREDENTIALS')
        format_mock.assert_called_once_with('CREDENTIALS', prefix='export ')

    @patch('os.name', 'nt')
    @patch('afp_cli.exporters.format_aws_credentials')
    def test_print_export_nt(self, format_mock):
        print_export('CREDENTIALS')
        format_mock.assert_called_once_with('CREDENTIALS', prefix='set ')


class SubShellTests(TestCase):

    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    def test_start_subshell(self, call_mock, tempfile_mock):
        memfile = StringIO()
        memfile.name = 'FILENAME'
        tempfile_mock.return_value = memfile
        credentials = {'AWS_VALID_SECONDS': 600}
        start_subshell(credentials, 'ACCOUNT', 'ROLE')
        call_mock.assert_called_once_with(
            ["bash", "--rcfile", 'FILENAME'],
            stdout=sys.stdout, stderr=sys.stderr, stdin=sys.stdin)
        expected = dedent("""
            # Pretend to be an interactive, non-login shell
            for file in /etc/bash.bashrc ~/.bashrc; do
                [ -f "$file" ] && . "$file"
            done

            function afp_minutes_left {
                if ((SECONDS >= 600)) ; then
                    echo EXPIRED
                else
                    echo $(((600-SECONDS)/60)) Min
                fi
            }

            PS1="(AWS ACCOUNT/ROLE \$(afp_minutes_left)) $PS1"
            export AWS_VALID_SECONDS='600'""")
        memfile.seek(0)
        received = memfile.read()
        self.assertEqual(received, expected)

    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    @patch('os.unlink')
    def test_start_subcmd(self, unlink_mock, call_mock, tempfile_mock):
        memfile = StringIO()
        memfile.name = 'FILENAME'
        # Need to mock away the 'close', so we can read it out later
        # despite 'close' being called inside the function.
        memfile.close = Mock()
        tempfile_mock.return_value = memfile
        credentials = {'AWS_VALID_SECONDS': 600}
        start_subcmd(credentials, 'ACCOUNT', 'ROLE')
        call_mock.assert_called_once_with(
            ["cmd", "/K", 'FILENAME'])
        expected = dedent("""
            @echo off
            set PROMPT=$C AWS ACCOUNT/ROLE $F
            set AWS_VALID_SECONDS='600'""")
        memfile.seek(0)
        received = memfile.read()
        self.assertEqual(received, expected)

    @patch('os.name', 'unix')
    @patch('afp_cli.exporters.start_subshell')
    def test_start_subx_unix(self, format_mock):
        credentials = {'AWS_VALID_SECONDS': 600}
        enter_subx(credentials, 'ACCOUNT', 'ROLE')

    @patch('os.name', 'nt')
    @patch('afp_cli.exporters.start_subcmd')
    def test_start_subx_nt(self, format_mock):
        credentials = {'AWS_VALID_SECONDS': 600}
        enter_subx(credentials, 'ACCOUNT', 'ROLE')
