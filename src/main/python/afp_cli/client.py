#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals, division

import requests
import json
from requests.auth import HTTPBasicAuth


class AWSFederationClientCmd(object):
    """Class for a command line client which uses the afp api"""

    def __init__(self, *args, **kwargs):
        self.username = kwargs.get('username', None)
        self._password = kwargs.get('password', None)
        self.api_url = kwargs.get('api_url', None)
        self.ssl_verify = kwargs.get('ssl_verify', True)

    def call_api(self, url_suffix):
        """Send a request to the aws federation proxy"""
        # TODO: Automatic versioning instead of the static below
        headers = {'User-Agent': 'afp-cli/1.0.6'}
        api_result = requests.get('{0}{1}'.format(self.api_url, url_suffix),
                                  headers=headers,
                                  verify=self.ssl_verify,
                                  auth=HTTPBasicAuth(self.username,
                                                     self._password))
        if api_result.status_code != 200:
            if api_result.status_code == 401:
                raise Exception("API call to AWS (%s/%s) failed: %s %s" % (
                    self.api_url, url_suffix, api_result.status_code, api_result.reason))
            else:
                raise Exception("API call to AWS (%s/%s) failed: %s" % (
                    self.api_url, url_suffix, api_result.json()['message']))
        return api_result.text

    def get_account_and_role_list(self):
        """Create an aws federation proxy request and return the result"""
        accounts_and_roles = self.call_api("/account")
        return json.loads(accounts_and_roles)

    def get_aws_credentials(self, account, role):
        """Return AWS credentials for a specified user and account"""
        aws_credentials = self.call_api("/account/{0}/{1}".format(account,
                                                                  role))
        aws_credentials = json.loads(aws_credentials)
        return {'AWS_ACCESS_KEY_ID': aws_credentials['AccessKeyId'],
                'AWS_SECRET_ACCESS_KEY': aws_credentials['SecretAccessKey'],
                'AWS_SESSION_TOKEN': aws_credentials['Token'],
                'AWS_SECURITY_TOKEN': aws_credentials['Token'],
                'AWS_EXPIRATION_DATE': aws_credentials['Expiration']}

    def print_account_and_role_list(self):
        """Print account and role list to stdout"""
        accounts_and_roles = sorted(self.get_account_and_role_list().items())
        for account, roles in accounts_and_roles:
            role_string = ",".join(sorted(roles))
            print("{0:<20} {1}".format(account, role_string))

    def print_aws_credentials_with_export_style(self, account, role):
        """Print aws credentials for account and role as bash export command"""
        for key, value in self.get_aws_credentials(account, role).items():
            print("export {0}={1}".format(key, value))
