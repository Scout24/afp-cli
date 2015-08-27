AFP CLI
**************************

Overview
========
The AFP CLI is the command line interface to access the AWS Federation Proxy.

Its main use case is starting a new shell where your temporary AWS
credentials have been exported into the environment.


Configuration
~~~~~~~~~~~~~

The **afp-cli** command can be globally configured with a yaml file:
    ``/etc/aws-federation-client/api.yaml``

Syntax:
    ``api_url: <api-url>``

Each user's home directory can override this setting in the same way, using
    ``$HOME/.aws-federation-client/api.yaml``


CLI Tool
========

Get help text
~~~~~~~~~~~~~~~~~~~~~~
    ``aws-cli [-h | --help]``

List available account names and roles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For the currently logged-in user:
    ``aws-cli``

The same for another user:
    ``aws-cli --user=username``

Output format:
    ``<accountname>    <role1>,<role2>,...,<roleN>``

Example output::

    abc_account     some_role_in_abc_account
    xyz_account     some_role_in_yxz_account,another_role_in_xyz

Export credentials
~~~~~~~~~~~~~~~~~~
This starts a subshell in which the credentials have been exported into the environment. Use
the "exit" command or press CTRL+D to terminate the subshell.

Export credentials for currently logged in user and specified account and role
    ``afp-cli --account=accountname --role=rolename``

As above, but specifying a different user:
    ``afp-cli --user=username --account=accountname --role=rolename``

Specify the URL of the AFP server, overriding any config file
    ``afp-cli --api-url=https://yourhost/some/path .....``

