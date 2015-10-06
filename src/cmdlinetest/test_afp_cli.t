#!/usr/bin/env cram
# vim: set syntax=cram :

  $ export PROJECT_ROOT=$TESTDIR/../../
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

  $ afp --no-ask-pw --api-url=http://localhost:5555 
  Failed to get account list from AWS: ('Connection aborted.', error(111, 'Connection refused'))
  [1]
