=======
AFP CLI
=======

.. image:: https://travis-ci.org/ImmobilienScout24/afp-cli.png?branch=master
   :alt: Travis build status image
   :align: left
   :target: https://travis-ci.org/ImmobilienScout24/afp-cli

Overview
========

The AFP CLI is the command line interface to access the
AWS Federation Proxy (AFP).

Its main use case is starting a new shell where your temporary
AWS credentials have been exported into the environment.

Configuration
=============

The **afp** command can be configured through yaml files in
the following direcories:

* ``/etc/afp-cli/*.yaml`` (global configuration)
* ``$HOME/.afp-cli/*.yaml`` (per-user configuration)

The yaml files are read in lexical order and merged via
`yamlreader <https://github.com/ImmobilienScout24/yamlreader>`_.
The following configuration options are supported:

* ``api_url: <api-url>``
  Defaults to lookup a FQDN of a host named **afp** via DNS and construct
  the server url from it: ``https://{FQDN}/afp-api/latest``
* ``user: <username>``
  Defaults to the currently logged in username

Example:

.. code-block:: yaml

    api_url: https://afp-server.my.domain/afp-api/latest
    user: myuser

CLI Tool
========

Get help text
-------------

.. code-block:: console

    $ afp [-h | --help]

List available account names and roles
--------------------------------------

For the currently logged-in user:

.. code-block:: console

    $ afp

The same for another user:

.. code-block:: console

    $ afp --user=username

Output format:

::

    <accountname>    <role1>,<role2>,...,<roleN>

Example output:

::

    abc_account    some_role_in_abc_account
    xyz_account    some_role_in_yxz_account,another_role_in_xyz

Use AWS credentials
-------------------

This starts a subshell in which the credentials have been exported into the
environment. Use the **exit** command or press **CTRL+D** to terminate the subshell.

Use credentials for currently logged in user and specified account and role:

.. code-block:: console

    $ afp accountname rolename

Use credentials for the currently logged in user for the *first* role:

.. code-block:: console

    $ afp accountname

As above, but specifying a different user:

.. code-block:: console

    $ afp --user=username accountname rolename

Specify the URL of the AFP server, overriding any config file:

.. code-block:: console

    $ afp --api-url=https://yourhost/some/path
