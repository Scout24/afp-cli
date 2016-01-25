=======
AFP CLI
=======

.. image:: https://travis-ci.org/ImmobilienScout24/afp-cli.png?branch=master
   :alt: Travis build status image
   :target: https://travis-ci.org/ImmobilienScout24/afp-cli

.. image:: https://coveralls.io/repos/ImmobilienScout24/afp-cli/badge.png?branch=master
    :alt: Coverage status
    :target: https://coveralls.io/r/ImmobilienScout24/afp-cli?branch=master

.. image:: https://img.shields.io/pypi/v/afp-cli.svg
   :alt: Version
   :target: https://pypi.python.org/pypi/afp-cli

Overview
========

The AFP CLI is the command line interface to access the
AWS Federation Proxy (AFP).

Its main use case is starting a new shell where your temporary
AWS credentials have been exported into the environment.

Installation
============

The tool is `hosted on PyPi <https://pypi.python.org/pypi/afp-cli>`_ and can be
installed using the usual Python specific mechanisms, e.g.:

.. code-block:: console

   $ pip install afp-cli

Configuration
=============

The ``afp`` command can be configured through yaml files in
the following directories:

* ``/etc/afp-cli/*.yaml`` (global configuration)
* ``$HOME/.afp-cli/*.yaml`` (per-user configuration)

The yaml files are read in lexical order and merged via
`yamlreader <https://github.com/ImmobilienScout24/yamlreader>`_.
The following configuration options are supported:

* ``api_url: <api-url>``
  Defaults to lookup a FQDN of a host named ``afp`` via DNS and construct
  the server url from it: ``https://{FQDN}/afp-api/latest``
  The specified url must contain full server url (not just the FQDN).
* ``user: <username>``
  Defaults to the currently logged in user-name

Example:

.. code-block:: yaml

    api_url: https://afp-server.my.domain/afp-api/latest
    user: myuser

Usage
=====

Get Help Text
-------------

.. code-block:: console

    $ afp [-h | --help]

List Available Account Names and Roles
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

Obtain AWS Credentials
----------------------

This starts a subshell in which the credentials have been exported into the
environment. Use the ``exit`` command or press **CTRL+D** to terminate the
subshell.

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

    $ afp --api-url=https://afp-server.my.domain/afp-api/latest

Show and Export
---------------

In case you don't want to start a subshell or are using something other than
bash, you can use ``--show`` or ``--export`` to display the credentials. You
can use the usual UNIX tools to add/remove them from your environment.
``--show`` will just show them and ``--export`` will show them in a format
suitable for an export into your environment, i.e. prefixed with ``export`` for
UNIX and ``set`` for Windows.


.. code-block:: console

   $ afp --show <myaccount> [<myrole>]
   Password for myuser:
   AWS_VALID_SECONDS='600'
   AWS_SESSION_TOKEN='XXX'
   AWS_SECURITY_TOKEN='XXX'
   AWS_SECRET_ACCESS_KEY='XXX'
   AWS_EXPIRATION_DATE='1970-01-01T01:00:00Z'
   AWS_ACCESS_KEY_ID='XXX'

.. code-block:: console

   $ afp --export <myaccount> [<myrole>]
   Password for myuser:
   export AWS_VALID_SECONDS='600'
   export AWS_SESSION_TOKEN='XXX'
   export AWS_SECURITY_TOKEN='XXX'
   export AWS_SECRET_ACCESS_KEY='XXX'
   export AWS_EXPIRATION_DATE='1970-01-01T01:00:00Z'
   export AWS_ACCESS_KEY_ID='XXX'


The following examples work in zsh, to add and remove them from your
environment:

Adding credentials:

.. code-block:: console

   $ eval $(afp --export <accountname>)

Removing them again:

.. code-block:: console

    $ env | grep AWS | cut -f 1 -d'=' | while read line ; do ; unset $line ; done ;

Write to AWS Credentials File
-----------------------------

The AWS tools reads credentials specified with ``aws configure`` from a local
file named ``credentials`` in a folder named ``.aws`` in your home directory.
The afp-cli tool can write your temporary credentials to this file.

.. code-block:: console

   $ afp --write <myaccount> [<myrole>]

Configuration Settings and Precedence
-------------------------------------

Please read the section on `Configuration Settings and Precedence
<https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#config-settings-and-precedence>`_
from the AWS documentation.

Interface with the System Keyring
---------------------------------

Staring with version ``1.3.0`` experimental support for the `Python keyring
module <https://pypi.python.org/pypi/keyring>`_ has been implemented. This has
been tested with the Gnome Keyring and Max OS X Keychain but supposedly also
works with Windows Credential Vault. Note: you need to additionally install the
``keyring`` module, for example using:

.. code-block:: console

   $ pip install keyring

You can configure to use the keychain by config-file or command-line switch.
Viable options are: ``prompt`` to prompt for the password during every
interaction with the AFP server. ``keyring`` to use the
Python ``keyring`` module. And ``testing``, which will simply send
the hardcoded string ``PASSWORD`` every time. As the name suggests, this is
only useful for testing.

Example config-file:

.. code-block:: yaml

    user: myuser
    password-provider: keyring

Example command-line:

.. code-block:: console

   $ afp --password-provider keyring
   No password found in keychain, please enter it now to store it.
   Password for vhaenel: 

As you can see, you will be prompted for your password the first time. Note
that if you fail to enter the password correctly, the incorrect version will be
stored. Note further that if you are using the Gnome-Keychain you can use the
tool ``seahorse`` to update and delete saved passwords, in this case for the
service ``afp``.


There are two intricate caveats when using the ``keyring`` module with
Gnome-Keychain which is why this feature is considered experimental.

In order for the module to correctly use the Gnome Keychain the Python module
`PyGObject aka gi
<https://wiki.gnome.org/action/show/Projects/PyGObject?action=show&redirect=PyGObject>`_
is required. As stated on the project website: "PyGObject is a Python extension
module that gives clean and consistent access to the entire GNOME software
platform through the use of GObject Introspection." Now, unfortunately, even
though this project is `available on PyPi
<https://pypi.python.org/pypi/PyGObject>`_ it can not be installed from there
using ``pip`` due to issues with the build system. It is however available as a
system package for Ubuntu distributions as package ``python-gi``. Long story
short; in order to use the ``keyring`` module from ``afp-cli`` you need to
have the ``gi`` module available to your Python interpreter. You can achieve
this, for example, by doing a global install of ``afp-cli`` using something
like ``sudo pip install afp-cli`` or install it into a virtual environment that
uses the system site packages because it has been created with the
``--system-site-packages`` flag.

A second issue arises when the ``gi`` module is not installed. In this case,
the ``keyring`` library simply selects an insecure ``PlaintextKeyring`` which
simply stores the base64 encoded password in it's default location at:
``~/.local/share/python_keyring/keyring_pass.cfg`` (!). Since we prefer a
secure-by-default approach, the ``afp-cli`` will abort with an appropriate
message in case this backend is detected.

Lastly, you can use the ``debug`` switch to check at runtime which backend was
selected:

.. code:: console

    $ afp-cli --debug --password-provider keychain
    ...
    Note: will use the backend: '<keyring.backends.Gnome.Keyring object at 0x7f48a13e9510>'
    ...

License
=======

Copyright 2015,2016 Immobilien Scout GmbH

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

See Also
========

See Hologram_ for another solution that brings temporary AWS credentials onto
developer desktops.

.. _Hologram: https://github.com/AdRoll/hologram
