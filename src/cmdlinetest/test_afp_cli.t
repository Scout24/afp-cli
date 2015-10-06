#!/usr/bin/env cram
# vim: set syntax=cram :

  $ export PROJECT_ROOT=$TESTDIR/../../
  $ cp $TESTDIR/afp_mock.py .

# Test help

  $ afp -h
  Command line client for the AFP (AWS Federation Proxy)
  
  Usage:
      afp [--debug] [--user=<username>] [--no-ask-pw] [--api-url=<api url>]
                                [--show | --export ] [(<accountname> [<rolename>])]
  
  Options:
    -h --help                Show this.
    --debug                  Activate debug output.
    --user=<username>        The user you want to use.
    --api-url=<api url>      The URL of the AFP server.
    --show                   Show credentials instead of opening subshell.
    --export                 Show credentials in an export suitable format.
    --no-ask-pw              Don't promt for password (for testing only).
    <accountname>            The AWS account id you want to login to.
    <rolename>               The AWS role you want to use for login. Defaults to the first role.

# Test failing to access AFP

  $ afp --no-ask-pw --api-url=http://localhost:5555 
  Failed to get account list from AWS: ('Connection aborted.', error(111, 'Connection refused'))
  [1]

# Test failing to access AFP with debug

  $ afp --debug --no-ask-pw --api-url=http://localhost:5555 
  Failed to get account list from AWS: ('Connection aborted.', error(111, 'Connection refused'))
  {u'--api-url': 'http://localhost:5555',
   u'--debug': True,
   u'--export': False,
   u'--no-ask-pw': True,
   u'--show': False,
   u'--user': None,
   u'<accountname>': None,
   u'<rolename>': None,
   u'url>': False}
  [1]

# BEGIN mocking AFP

  $ ./afp_mock.py start
  $ sleep 1

# Test get account and role

  $ afp --no-ask-pw --api-url=http://localhost:5555
  test_account         test_role

# Test credentials with subshell

  $ afp --no-ask-pw --api-url=http://localhost:5555 test_account test_role
  Entering AFP subshell for account test_account, role test_role.
  Press CTRL+D to exit.
  Left AFP subshell.


# Test credentials with show

  $ afp --no-ask-pw --api-url=http://localhost:5555 --show test_account test_role
  AWS_VALID_SECONDS='.*' (re)
  AWS_SESSION_TOKEN='XXXXXXXXXXXX'
  AWS_SECURITY_TOKEN='XXXXXXXXXXXX'
  AWS_SECRET_ACCESS_KEY='XXXXXXXXXXXX'
  AWS_EXPIRATION_DATE='2032-01-01T00:00:00Z'
  AWS_ACCESS_KEY_ID='XXXXXXXXXXXX'

# Test credentials with show and only a single role

  $ afp --no-ask-pw --api-url=http://localhost:5555 --show test_account
  AWS_VALID_SECONDS='.*' (re)
  AWS_SESSION_TOKEN='XXXXXXXXXXXX'
  AWS_SECURITY_TOKEN='XXXXXXXXXXXX'
  AWS_SECRET_ACCESS_KEY='XXXXXXXXXXXX'
  AWS_EXPIRATION_DATE='2032-01-01T00:00:00Z'
  AWS_ACCESS_KEY_ID='XXXXXXXXXXXX'

# Test credentials with export

  $ afp --no-ask-pw --api-url=http://localhost:5555 --export test_account test_role
  export AWS_VALID_SECONDS='.*' (re)
  export AWS_SESSION_TOKEN='XXXXXXXXXXXX'
  export AWS_SECURITY_TOKEN='XXXXXXXXXXXX'
  export AWS_SECRET_ACCESS_KEY='XXXXXXXXXXXX'
  export AWS_EXPIRATION_DATE='2032-01-01T00:00:00Z'
  export AWS_ACCESS_KEY_ID='XXXXXXXXXXXX'

# END mocking AFP


  $ ./afp_mock.py stop
