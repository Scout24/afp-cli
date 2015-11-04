#!/usr/bin/env python
""" Simple AFP mock to allow testing the afp-cli. """

import bottle
from bottle import route
from textwrap import dedent
from bottledaemon import daemon_run
import sys


@route('/account')
def account():
    return """{"test_account": ["test_role"]}"""


@route('/account/<account>/<role>')
def credentials(account, role):
    return dedent("""
                  {"Code": "Success",
                   "LastUpdated": "1970-01-01T00:00:00Z",
                   "AccessKeyId": "XXXXXXXXXXXX",
                   "SecretAccessKey": "XXXXXXXXXXXX",
                   "Token": "XXXXXXXXXXXX",
                   "Expiration": "2032-01-01T00:00:00Z",
                   "Type": "AWS-HMAC"}""").strip()

if len(sys.argv) > 1:
    daemon_run(host='localhost', port=5555)
else:
    # manual testing mode on different port, so it won't stop "pyb install" from running tests
    bottle.run(host='localhost', port=5544)
