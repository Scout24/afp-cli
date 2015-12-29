#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest2 import TestCase
from afp_cli import aws_credentials_file
import tempfile
import shutil
import os


class AwsCredentialsFileTest(TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_write_default_profile_to_new_file(self):
        credentials_filename = os.path.join(self.tempdir, 'credentials')
        aws_credentials_file.write({
            'AWS_ACCESS_KEY_ID': 'AccessKeyId',
            'AWS_SECRET_ACCESS_KEY': 'SecretAccessKey',
            'AWS_SESSION_TOKEN': 'Token',
            'AWS_SECURITY_TOKEN': 'Token',
            'AWS_EXPIRATION_DATE': 'Expiration'
        }, credentials_filename)

        self.assertEqual(open(credentials_filename).read(), (
            '[default]\n'
            'aws_access_key_id = AccessKeyId\n'
            'aws_secret_access_key = SecretAccessKey\n'
            'aws_session_token = Token\n'
            'aws_security_token = Token\n\n'
        ))

    def test_write_default_profile_to_new_file_in_not_existing_directory(self):
        credentials_filename = os.path.join(self.tempdir, '.aws/credentials')
        aws_credentials_file.write({
            'AWS_ACCESS_KEY_ID': 'AccessKeyId',
            'AWS_SECRET_ACCESS_KEY': 'SecretAccessKey',
            'AWS_SESSION_TOKEN': 'Token',
            'AWS_SECURITY_TOKEN': 'Token',
            'AWS_EXPIRATION_DATE': 'Expiration'
        }, credentials_filename)

        self.assertEqual(open(credentials_filename).read(), (
            '[default]\n'
            'aws_access_key_id = AccessKeyId\n'
            'aws_secret_access_key = SecretAccessKey\n'
            'aws_session_token = Token\n'
            'aws_security_token = Token\n\n'
        ))

    def test_overwrite_default_profile(self):
        credentials_filename = os.path.join(self.tempdir, 'credentials')
        with open(credentials_filename, "w") as credentials_file:
            credentials_file.write((
                '[default]\n'
                'aws_access_key_id = AccessKeyIdToOverwrite\n'
                'aws_secret_access_key = SecretAccessKeyToOverwrite\n'
                'aws_session_token = TokenToOverwrite\n'
                'aws_security_token = TokenToOverwrite\n\n'
            ))

        aws_credentials_file.write({
            'AWS_ACCESS_KEY_ID': 'AccessKeyId',
            'AWS_SECRET_ACCESS_KEY': 'SecretAccessKey',
            'AWS_SESSION_TOKEN': 'Token',
            'AWS_SECURITY_TOKEN': 'Token',
            'AWS_EXPIRATION_DATE': 'Expiration'
        }, credentials_filename)

        self.assertEqual(open(credentials_filename).read(), (
            '[default]\n'
            'aws_access_key_id = AccessKeyId\n'
            'aws_secret_access_key = SecretAccessKey\n'
            'aws_session_token = Token\n'
            'aws_security_token = Token\n\n'
        ))

    def test_write_profile_to_new_file(self):
        credentials_filename = os.path.join(self.tempdir, 'credentials')
        aws_credentials_file.write({
            'AWS_ACCESS_KEY_ID': 'AccessKeyId',
            'AWS_SECRET_ACCESS_KEY': 'SecretAccessKey',
            'AWS_SESSION_TOKEN': 'Token',
            'AWS_SECURITY_TOKEN': 'Token',
            'AWS_EXPIRATION_DATE': 'Expiration'
        }, credentials_filename, 'profile')

        self.assertEqual(open(credentials_filename).read(), (
            '[profile]\n'
            'aws_access_key_id = AccessKeyId\n'
            'aws_secret_access_key = SecretAccessKey\n'
            'aws_session_token = Token\n'
            'aws_security_token = Token\n\n'
        ))

    def test_add_profile(self):
        credentials_filename = os.path.join(self.tempdir, 'credentials')
        with open(credentials_filename, "w") as credentials_file:
            credentials_file.write((
                '[default]\n'
                'aws_access_key_id = defaultAccessKeyId\n'
                'aws_secret_access_key = defaultSecretAccessKey\n'
                'aws_session_token = defaultToken\n'
                'aws_security_token = defaultToken\n\n'
                '[profile]\n'
                'aws_access_key_id = profileAccessKeyId\n'
                'aws_secret_access_key = profileSecretAccessKey\n'
                'aws_session_token = profileToken\n'
                'aws_security_token = profileToken\n\n'
            ))

        aws_credentials_file.write({
            'AWS_ACCESS_KEY_ID': 'AccessKeyId',
            'AWS_SECRET_ACCESS_KEY': 'SecretAccessKey',
            'AWS_SESSION_TOKEN': 'Token',
            'AWS_SECURITY_TOKEN': 'Token',
            'AWS_EXPIRATION_DATE': 'Expiration'
        }, credentials_filename, 'new-profile')

        self.assertEqual(open(credentials_filename).read(), (
            '[default]\n'
            'aws_access_key_id = defaultAccessKeyId\n'
            'aws_secret_access_key = defaultSecretAccessKey\n'
            'aws_session_token = defaultToken\n'
            'aws_security_token = defaultToken\n\n'
            '[profile]\n'
            'aws_access_key_id = profileAccessKeyId\n'
            'aws_secret_access_key = profileSecretAccessKey\n'
            'aws_session_token = profileToken\n'
            'aws_security_token = profileToken\n\n'
            '[new-profile]\n'
            'aws_access_key_id = AccessKeyId\n'
            'aws_secret_access_key = SecretAccessKey\n'
            'aws_session_token = Token\n'
            'aws_security_token = Token\n\n'
        ))

    def test_overwrite_profile(self):
        credentials_filename = os.path.join(self.tempdir, 'credentials')
        with open(credentials_filename, "w") as credentials_file:
            credentials_file.write((
                '[default]\n'
                'aws_access_key_id = defaultAccessKeyId\n'
                'aws_secret_access_key = defaultSecretAccessKey\n'
                'aws_session_token = defaultToken\n'
                'aws_security_token = defaultToken\n\n'
                '[profile-to-overwrite]\n'
                'aws_access_key_id = profileAccessKeyIdToOverwrite\n'
                'aws_secret_access_key = profileSecretAccessKeyToOverwrite\n'
                'aws_session_token = profileTokenToOverwrite\n'
                'aws_security_token = profileTokenToOverwrite\n\n'
            ))

        aws_credentials_file.write({
            'AWS_ACCESS_KEY_ID': 'AccessKeyId',
            'AWS_SECRET_ACCESS_KEY': 'SecretAccessKey',
            'AWS_SESSION_TOKEN': 'Token',
            'AWS_SECURITY_TOKEN': 'Token',
            'AWS_EXPIRATION_DATE': 'Expiration'
        }, credentials_filename, 'profile-to-overwrite')

        self.assertEqual(open(credentials_filename).read(), (
            '[default]\n'
            'aws_access_key_id = defaultAccessKeyId\n'
            'aws_secret_access_key = defaultSecretAccessKey\n'
            'aws_session_token = defaultToken\n'
            'aws_security_token = defaultToken\n\n'
            '[profile-to-overwrite]\n'
            'aws_access_key_id = AccessKeyId\n'
            'aws_secret_access_key = SecretAccessKey\n'
            'aws_session_token = Token\n'
            'aws_security_token = Token\n\n'
        ))
