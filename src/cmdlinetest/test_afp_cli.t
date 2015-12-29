#!/usr/bin/env cram
# vim: set syntax=cram :

# These are the cram tests for the afp-cli. Since the tool prompts for a
# password and needs to connect to a server, both these things have to be
# mocked away. As for the password, we use the '--no-ask-pw' flag which will
# simply not prompt for a password. For the server, we included a minimal
# bottle based AFP mock that only responds to two API endpoints.

  $ export PROJECT_ROOT=$TESTDIR/../../
  $ cp $TESTDIR/afp_mock.py .
  $ ls
  afp_mock.py

# Test help

  $ afp -h
  Command line client for the AFP (AWS Federation Proxy)
  
  Usage:
      afp [--debug] [--user=<username>] [--password-provider=<provider>] [--api-url=<api-url>]
                                [--show | --export | --write] [(<accountname> [<rolename>])]
  
  Options:
    -h --help                       Show this.
    --debug                         Activate debug output.
    --user=<username>               The user you want to use.
    --api-url=<api-url>             The URL of the AFP server (e.g. https://afp/afp-api/latest).
    --show                          Show credentials instead of opening subshell.
    --export                        Show credentials in an export suitable format.
    --write                         Write credentials to aws credentials file.
    --password-provider=<provider>  Password provider.
    <accountname>                   The AWS account id you want to login to.
    <rolename>                      The AWS role you want to use for login. Defaults to the first role.

# Test failing to access AFP

  $ afp --password-provider testing --api-url=http://localhost:5555
  Failed to get account list from AWS: .* (re)
  [1]

  $ afp --password-provider no_such_provider --api-url=http://localhost:5555
  'no_such_provider' is not a valid password provider.
  Valid options are: ['prompt', 'keyring', 'testing']
  [1]

# Test failing to access AFP with debug

  $ afp --debug --password-provider testing --api-url=http://localhost:5555
  Failed to get account list from AWS: .* (re)
  {u?'--api-url': 'http://localhost:5555', (re)
   u?'--debug': True, (re)
   u?'--export': False, (re)
   u?'--password-provider': 'testing', (re)
   u?'--show': False, (re)
   u?'--user': None, (re)
   u?'--write': False, (re)
   u?'<accountname>': None, (re)
   u?'<rolename>': None} (re)
  [1]

# Test failing to access AFP with debug and username

  $ afp --debug --password-provider testing --api-url=http://localhost:5555 --user=test_user
  Failed to get account list from AWS: .* (re)
  {u?'--api-url': 'http://localhost:5555', (re)
   u?'--debug': True, (re)
   u?'--export': False, (re)
   u?'--password-provider': 'testing', (re)
   u?'--show': False, (re)
   u?'--user': 'test_user', (re)
   u?'--write': False, (re)
   u?'<accountname>': None, (re)
   u?'<rolename>': None} (re)
  [1]

# BEGIN mocking AFP

  $ ./afp_mock.py start
  $ sleep 1
  $ ls bottle.*
  bottle.log
  bottle.pid
  bottle.pid.lock

# Test get account and role

  $ afp --password-provider testing --api-url=http://localhost:5555
  test_account         test_role

# Test credentials with subshell

  $ afp --password-provider testing --api-url=http://localhost:5555 test_account test_role < /dev/null
  Entering AFP subshell for account test_account, role test_role.
  Press CTRL+D to exit.
  Left AFP subshell.


# Test credentials with show

  $ afp --password-provider testing --api-url=http://localhost:5555 --show test_account test_role
  AWS_ACCESS_KEY_ID='XXXXXXXXXXXX'
  AWS_ACCOUNT_NAME='test_account'
  AWS_ASSUMED_ROLE='test_role'
  AWS_EXPIRATION_DATE='2032-01-01T00:00:00Z'
  AWS_SECRET_ACCESS_KEY='XXXXXXXXXXXX'
  AWS_SECURITY_TOKEN='XXXXXXXXXXXX'
  AWS_SESSION_TOKEN='XXXXXXXXXXXX'
  AWS_VALID_SECONDS='.*' (re)

# Test credentials with show and only a single role

  $ afp --password-provider testing --api-url=http://localhost:5555 --show test_account
  AWS_ACCESS_KEY_ID='XXXXXXXXXXXX'
  AWS_ACCOUNT_NAME='test_account'
  AWS_ASSUMED_ROLE='test_role'
  AWS_EXPIRATION_DATE='2032-01-01T00:00:00Z'
  AWS_SECRET_ACCESS_KEY='XXXXXXXXXXXX'
  AWS_SECURITY_TOKEN='XXXXXXXXXXXX'
  AWS_SESSION_TOKEN='XXXXXXXXXXXX'
  AWS_VALID_SECONDS='.*' (re)

# Test credentials with export

  $ afp --password-provider testing --api-url=http://localhost:5555 --export test_account test_role
  export AWS_ACCESS_KEY_ID='XXXXXXXXXXXX'
  export AWS_ACCOUNT_NAME='test_account'
  export AWS_ASSUMED_ROLE='test_role'
  export AWS_EXPIRATION_DATE='2032-01-01T00:00:00Z'
  export AWS_SECRET_ACCESS_KEY='XXXXXXXXXXXX'
  export AWS_SECURITY_TOKEN='XXXXXXXXXXXX'
  export AWS_SESSION_TOKEN='XXXXXXXXXXXX'
  export AWS_VALID_SECONDS='.*' (re)

# Test write credentials to file

  $ export HOME=$CRAMTMP
  $ afp --password-provider testing --api-url=http://localhost:5555 --write test_account test_role
  $ cat $HOME/.aws/credentials
  [default]
  aws_access_key_id = XXXXXXXXXXXX
  aws_secret_access_key = XXXXXXXXXXXX
  aws_session_token = XXXXXXXXXXXX
  aws_security_token = XXXXXXXXXXXX
  * (glob)

# END mocking AFP

  $ ./afp_mock.py stop
  $ ls
  afp_mock.py
  bottle.log
