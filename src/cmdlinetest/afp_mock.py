#!/usr/bin/env python
from bottle import route, run, response
from bottledaemon import daemon_run
from textwrap import dedent


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
daemon_run(host='localhost', port=5555)
#run(host='localhost', port=5555)
