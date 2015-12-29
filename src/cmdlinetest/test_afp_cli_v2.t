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

# Setup an alias, so that we can easily migrate tests later on.

  $ alias afp=afpv2

# Rewire users home directory, so we don't source data from there

  $ export HOME=$CRAMTMP

# Test help

  $ afp
  Usage:
      afp [options] help
      afp [options] version
      afp [options] list
      afp [options] (show | export | write | subshell) <accountname> [<rolename>]
  [1]

  $ afp -h
  Command line client for the AFP V2 (AWS Federation Proxy)
  
  Usage:
      afp [options] help
      afp [options] version
      afp [options] list
      afp [options] (show | export | write | subshell) <accountname> [<rolename>]
  
  Options:
    -h, --help                          Show this.
    -d, --debug                         Activate debug output.
    -u, --user <username>               The user you want to use.
    -a, --api-url <api-url>             The URL of the AFP server (e.g. https://afp/afp-api/latest).
    -p, --password-provider <provider>  Password provider. Valid values are: 'prompt', 'keyring' and 'testing'.
    <accountname>                       The AWS account id you want to login to.
    <rolename>                          The AWS role you want to use for login. Defaults to the first role.
  
  Subcommands:
    help                                Show help.
    version                             Show version.
    list                                List available accounts and roles.
    show                                Show credentials.
    export                              Show credentials in an export suitable format.
    write                               Write credentials to aws credentials file.
    subshell                            Open a subshell with exported credentials.

  $ afp --help
  Command line client for the AFP V2 (AWS Federation Proxy)
  
  Usage:
      afp [options] help
      afp [options] version
      afp [options] list
      afp [options] (show | export | write | subshell) <accountname> [<rolename>]
  
  Options:
    -h, --help                          Show this.
    -d, --debug                         Activate debug output.
    -u, --user <username>               The user you want to use.
    -a, --api-url <api-url>             The URL of the AFP server (e.g. https://afp/afp-api/latest).
    -p, --password-provider <provider>  Password provider. Valid values are: 'prompt', 'keyring' and 'testing'.
    <accountname>                       The AWS account id you want to login to.
    <rolename>                          The AWS role you want to use for login. Defaults to the first role.
  
  Subcommands:
    help                                Show help.
    version                             Show version.
    list                                List available accounts and roles.
    show                                Show credentials.
    export                              Show credentials in an export suitable format.
    write                               Write credentials to aws credentials file.
    subshell                            Open a subshell with exported credentials.

  $ afp help
  Command line client for the AFP V2 (AWS Federation Proxy)
  
  Usage:
      afp [options] help
      afp [options] version
      afp [options] list
      afp [options] (show | export | write | subshell) <accountname> [<rolename>]
  
  Options:
    -h, --help                          Show this.
    -d, --debug                         Activate debug output.
    -u, --user <username>               The user you want to use.
    -a, --api-url <api-url>             The URL of the AFP server (e.g. https://afp/afp-api/latest).
    -p, --password-provider <provider>  Password provider. Valid values are: 'prompt', 'keyring' and 'testing'.
    <accountname>                       The AWS account id you want to login to.
    <rolename>                          The AWS role you want to use for login. Defaults to the first role.
  
  Subcommands:
    help                                Show help.
    version                             Show version.
    list                                List available accounts and roles.
    show                                Show credentials.
    export                              Show credentials in an export suitable format.
    write                               Write credentials to aws credentials file.
    subshell                            Open a subshell with exported credentials.

# Test failing to access AFP

  $ afp -p testing -a http://localhost:5555 list
  Failed to get account list from AWS: .* (re)
  [1]

  $ afp -p no_such_provider -a http://localhost:5555 list
  'no_such_provider' is not a valid password provider.
  Valid options are: ['prompt', 'keyring', 'testing']
  [1]

# Test failing to access AFP with debug

  $ afp -d -p testing -a http://localhost:5555 list
  Failed to get account list from AWS: .* (re)
  {u?'--api-url': 'http://localhost:5555', (re)
   u?'--debug': True, (re)
   u?'--help': False, (re)
   u?'--password-provider': 'testing', (re)
   u?'--user': None, (re)
   u?'<accountname>': None, (re)
   u?'<rolename>': None, (re)
   u?'export': False, (re)
   u?'help': False, (re)
   u?'list': True, (re)
   u?'show': False, (re)
   u?'subshell': False, (re)
   u?'version': False, (re)
   u?'write': False} (re)
  Subcommand is 'list'
  'api-url' is 'http://localhost:5555'
  'username' is '.*' (re)
  'password-provider' is 'testing'
  [1]

# Test failing to access AFP with debug and username

  $ afp --debug --password-provider testing --api-url=http://localhost:5555 --user=test_user list
  Failed to get account list from AWS: .* (re)
  {u?'--api-url': 'http://localhost:5555', (re)
   u?'--debug': True, (re)
   u?'--help': False, (re)
   u?'--password-provider': 'testing', (re)
   u?'--user': 'test_user', (re)
   u?'<accountname>': None, (re)
   u?'<rolename>': None, (re)
   u?'export': False, (re)
   u?'help': False, (re)
   u?'list': True, (re)
   u?'show': False, (re)
   u?'subshell': False, (re)
   u?'version': False, (re)
   u?'write': False} (re)
  Subcommand is 'list'
  'api-url' is 'http://localhost:5555'
  'username' is 'test_user'
  'password-provider' is 'testing'
  [1]

# Test failing to access AFP with debug and username with long options

  $ afp -d -p testing -a http://localhost:5555 -u test_user list
  Failed to get account list from AWS: .* (re)
  {u?'--api-url': 'http://localhost:5555', (re)
   u?'--debug': True, (re)
   u?'--help': False, (re)
   u?'--password-provider': 'testing', (re)
   u?'--user': 'test_user', (re)
   u?'<accountname>': None, (re)
   u?'<rolename>': None, (re)
   u?'export': False, (re)
   u?'help': False, (re)
   u?'list': True, (re)
   u?'show': False, (re)
   u?'subshell': False, (re)
   u?'version': False, (re)
   u?'write': False} (re)
  Subcommand is 'list'
  'api-url' is 'http://localhost:5555'
  'username' is 'test_user'
  'password-provider' is 'testing'
  [1]

# BEGIN mocking AFP

  $ ./afp_mock.py start
  $ sleep 1
  $ ls bottle.*
  bottle.log
  bottle.pid
  bottle.pid.lock

# Test get account and role

  $ afp -p testing -a http://localhost:5555  list
  test_account         test_role

# Test credentials with subshell

  $ afp -p testing -a http://localhost:5555 subshell test_account test_role < /dev/null
  Entering AFP subshell for account test_account, role test_role.
  Press CTRL+D to exit.
  Left AFP subshell.


# Test credentials with show

  $ afp -p testing -a http://localhost:5555 show test_account test_role
  AWS_ACCESS_KEY_ID='XXXXXXXXXXXX'
  AWS_ACCOUNT_NAME='test_account'
  AWS_ASSUMED_ROLE='test_role'
  AWS_EXPIRATION_DATE='2032-01-01T00:00:00Z'
  AWS_SECRET_ACCESS_KEY='XXXXXXXXXXXX'
  AWS_SECURITY_TOKEN='XXXXXXXXXXXX'
  AWS_SESSION_TOKEN='XXXXXXXXXXXX'
  AWS_VALID_SECONDS='.*' (re)

# Test credentials with show and only a single role

  $ afp -p  testing -a http://localhost:5555 show test_account
  AWS_ACCESS_KEY_ID='XXXXXXXXXXXX'
  AWS_ACCOUNT_NAME='test_account'
  AWS_ASSUMED_ROLE='test_role'
  AWS_EXPIRATION_DATE='2032-01-01T00:00:00Z'
  AWS_SECRET_ACCESS_KEY='XXXXXXXXXXXX'
  AWS_SECURITY_TOKEN='XXXXXXXXXXXX'
  AWS_SESSION_TOKEN='XXXXXXXXXXXX'
  AWS_VALID_SECONDS='.*' (re)

# Test credentials with export

  $ afp -p testing -a http://localhost:5555 export test_account test_role
  export AWS_ACCESS_KEY_ID='XXXXXXXXXXXX'
  export AWS_ACCOUNT_NAME='test_account'
  export AWS_ASSUMED_ROLE='test_role'
  export AWS_EXPIRATION_DATE='2032-01-01T00:00:00Z'
  export AWS_SECRET_ACCESS_KEY='XXXXXXXXXXXX'
  export AWS_SECURITY_TOKEN='XXXXXXXXXXXX'
  export AWS_SESSION_TOKEN='XXXXXXXXXXXX'
  export AWS_VALID_SECONDS='.*' (re)

# Test write credentials to file

  $ afp -p testing -a http://localhost:5555 write test_account test_role
  $ cat $HOME/.aws/credentials
  [default]
  aws_access_key_id = XXXXXXXXXXXX
  aws_secret_access_key = XXXXXXXXXXXX
  aws_session_token = XXXXXXXXXXXX
  aws_security_token = XXXXXXXXXXXX
  


# END mocking AFP

  $ ./afp_mock.py stop
  $ ls
  afp_mock.py
  bottle.log
