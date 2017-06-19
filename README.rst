pdfebc-core - Core functions for the pdfebc tools
*************************************************

`Docs`_

.. image:: https://travis-ci.org/slarse/pdfebc-core.svg?branch=master
    :target: https://travis-ci.org/slarse/pdfebc-core
    :alt: Build Status
.. image:: https://codecov.io/gh/slarse/pdfebc-core/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/slarse/pdfebc-core
    :alt: Code Coverage
.. image:: https://readthedocs.org/projects/pdfebc-core/badge/?version=latest
    :target: http://pdfebc-core.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://badge.fury.io/py/pdfebc-core.svg
    :target: https://badge.fury.io/py/pdfebc-core
    :alt: PyPi Version
.. image:: https://img.shields.io/badge/python-3.6-blue.svg
    :target: https://badge.fury.io/py/pdfebc
    :alt: Supported Python Versions

.. contents::

Overview
========
``pdfebc`` is planned to be a set of tools for compressing PDF files to e-reader friendly sizes,
and optionally sending them via e-mail to for example a Kindle. This package contains the core
functions that may be utilized by different user interfaces. Currently, I am planning to create
a CLI, a web interface and a desktop GUI. This is very much a practice project for me, but one
that is alos useful to me (at least the CLI version, the others are just practice).

As an example use case, I mainly use ``pdfebc`` as an easy way to compress lecture slides and 
similar study materials, send them to my Kindle and then clean up the output.

Purpose of the project
======================
The core functionality of ``pdfebc``, along with a basic CLI, was already done when I started 
this little project. As such, the main purpose here isn't to provide the functionality,
but to do so in a robust way, with proper documentation, testing and continuous integration. 
This is also an exercise in writing a program's business logic in such a way so that any
interface can be slapped on top of it. This is also one of my first forays into using stuff like 
``sphinx``, ``Travis-CI`` and ``ReadTheDocs``, so there's bound to be some weirdness here and
there. I am also diving deeper into how to use ``git`` and trying new things, so the commit 
history may suffer from some inconsistencies.

Requirements
============
Aside from the Python omdules listed in `requirements.txt`_, the following requirements must be
met:

* Python 3.6
    - Strictly speaking, 3.5 should also work fine, but the tests use 3.6 features so the
      build is only tested for 3.6.
* ``Ghostscript``
    - ``pdfebc`` requires ``Ghostscript`` for the PDF compression. The default binary is ``gs``,
      but this can be specified via the CLI.
* A Gmail account (for sending e-mails)
    - By default, ``pdfebc`` uses Google's SMTP server to send e-mails. The program can however
      be configured to use any STMP server by maniupulating the ``config.cnf`` file (please see
      this `sample configuration`_ for formatting). Currently, the server must support TLS.

Install
=======
Option 1: Install from PyPi with ``pip``
----------------------------------------
The latest release of ``pdfebc-core`` is on PyPi, and can thus be installed as usual with ``pip``.
I strongly discourage system-wide ``pip`` installs (i.e. ``sudo pip install <package>``), as this
may land you with incompatible packages in a very short amount of time. A per-user install
can be done like this:

1. Execute ``pip install --user pdfebc-core`` to install the package.
2. Currently, you must add the configuration file manually. Please have a look at the
   `sample configuration`_ file for details. Where to put the configuration file is
   machine-dependent, and decided by the ``appdirs`` package. Run 
   ``apdirs.user_config_dir('pdfebc')`` in the Python interpreter to find the correct directory.
   Note that you must first import ``appdirs`` for it to be available in the interpreter.
   **Note:** When using a Gmail account, I strongly recommend
   using an `App password`_ instead of the actual account password.

Option 2: Clone the repo and the install with ``pip``
-----------------------------------------------------
If you want the dev version, you will need to clone the repo, as only release versions are uploaded
to PyPi. Unless you are planning to work on this yourself, I suggest going with the release version.

1. Clone the repo with ``git``:
    - ``git clone https://github.com/slarse/pdfebc-core``
2. ``cd`` into the project root directory and install with ``pip``.
    - ``pip install --user .``, this will create a local install for the current user.
    - Or just ``pip install .`` if you use ``virtualenv``.
    - For development, use ``pip install -e .`` in a ``virtualenv``.
3. Currently, you must add the configuration file manually. Please have a look at the
   `sample configuration`_ file for details. Where to put the configuration file is
   machine-dependent, and decided by the ``appdirs`` package. Run 
   ``apdirs.user_config_dir('pdfebc')`` in the Python interpreter to find the correct directory.
   Note that you must first import ``appdirs`` for it to be available in the interpreter.
   **Note:** When using a Gmail account, I strongly recommend
   using an `App password`_ instead of the actual account password.

License
=======
This software is licensed under the MIT License. See the `license file`_ file for specifics.

Contributing
============
I am currently not looking for contributions. At this point, this is a practice project for me,
and even if I were looking for outside help the test suite is nowhere near comprehensive enough
for that yet. Sorry!

.. _App password: https://support.google.com/accounts/answer/185833?hl=en
.. _license file: LICENSE
.. _sample configuration: config.cnf
.. _requirements.txt: requirements.txt
.. _Docs: https://pdfebc-core.readthedocs.io/en/latest/
