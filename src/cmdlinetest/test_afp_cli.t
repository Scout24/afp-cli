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
      afp [--debug] [--user=<username>] [--password-provider=<provider>] [--api-url=<api-url>] [--server <servername>]
                                [--show | --export | --write [--profile=<profile_name>]] [(<accountname> [<rolename>])]
  
  Options:
    -h --help                       Show this.
    -v --version                    Show version and exit.
    --debug                         Activate debug output.
    --user=<username>               The user you want to use.
    --server <servername>           The AFP server to use.
    --api-url=<api-url>             The URL of the AFP server (e.g. https://afp/afp-api/latest). Takes precedence over --server.
    --show                          Show credentials instead of opening subshell.
    --export                        Show credentials in an export suitable format.
    --write                         Write credentials to aws credentials file.
    --profile=<profile_name>        Which profile to use in the aws credentials file.
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
   u?'--profile': None, (re)
   u?'--server': None, (re)
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
   u?'--profile': None, (re)
   u?'--server': None, (re)
   u?'--show': False, (re)
   u?'--user': 'test_user', (re)
   u?'--write': False, (re)
   u?'<accountname>': None, (re)
   u?'<rolename>': None} (re)
  [1]

# BEGIN mocking AFP

  $ rm -f bottle.log
  $ ./afp_mock.py start
  $ sleep 1
# Log files in Python 2 contain bottle's greeting, in Python 3 the
# greeting is absent. Until we have https://github.com/brodie/cram/issues/14
# it is better to filter out the greeting via grep.
  $ grep -Ev 'server starting up|Listening on http|Hit Ctrl-C' bottle.log | grep -E ..; true

  $ ls bottle.*
  bottle.log
  bottle.pid
  bottle.pid.lock

# Test get account and role

  $ afp --password-provider testing --api-url=http://localhost:5555
  test_account                   test_role
  test_account_with_long_name    test_role_with_long_name

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
  Wrote credentials to file: '*/.aws/credentials' (glob)
  $ cat $HOME/.aws/credentials
  [default]
  aws_access_key_id = XXXXXXXXXXXX
  aws_secret_access_key = XXXXXXXXXXXX
  aws_session_token = XXXXXXXXXXXX
  aws_security_token = XXXXXXXXXXXX
  * (glob)

# Test write credentials to file with --profile

  $ export HOME=$CRAMTMP
  $ rm "$CRAMTMP/.aws/credentials"
  $ afp --password-provider testing --api-url=http://localhost:5555 --write --profile=foobar test_account test_role
  Wrote credentials to file: '*/.aws/credentials' (glob)
  $ cat $HOME/.aws/credentials
  [foobar]
  aws_access_key_id = XXXXXXXXXXXX
  aws_secret_access_key = XXXXXXXXXXXX
  aws_session_token = XXXXXXXXXXXX
  aws_security_token = XXXXXXXXXXXX
  * (glob)
  $ rm "$CRAMTMP/.aws/credentials"

# Output version of self

  $ afp --version
  afp-cli version * (glob)

  $ afp -v
  afp-cli version * (glob)

# END mocking AFP

  $ ./afp_mock.py stop
  $ ls
  afp_mock.py
  bottle.log
