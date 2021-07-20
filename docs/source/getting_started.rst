Getting Started
===============

These instructions will have the code running on your local or virtual
machine.

Requirements
~~~~~~~~~~~~

The :repo-main-file:`requirements.txt <requirements.txt>` indicates the required python
libraries. In short, you will need the following to have a working copy of
this software.
 1. Python (>=3.7.9)
 2. `ldap3`_ (2.6.1)
 3. `numpy`_ (1.20.0)
 4. :ual-re:`redata <redata-commons>` (>=0.3.2)
   a. `pandas`_ (1.2.3)
   b. `tabulate`_ (0.8.3)
   c. `requests`_ (2.25.1)


Installation Instructions
~~~~~~~~~~~~~~~~~~~~~~~~~

Python and setting up a ``conda`` environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, install a working version of Python (>=3.7.9). We recommend using
the `Anaconda`_ package installer.

After you have Anaconda installed, you will want to create a separate
``conda`` environment and activate it:

::

   $ (sudo) conda create -n figshare_patrons python=3.7
   $ conda activate figshare_patrons

Next, clone this repository into a parent folder:

::

   (figshare_patrons) $ cd /path/to/parent/folder
   (figshare_patrons) $ git clone https://github.com/UAL-RE/ReQUIAM.git

With the activated ``conda`` environment, you can install with the
``setup.py`` script:

::

   (figshare_patrons) $ cd /path/to/parent/folder/ReQUIAM
   (figshare_patrons) $ (sudo) python setup.py develop

This will automatically installed the required ``pandas``, ``ldap3``,
``requests``, and ``numpy`` packages.

You can confirm installation via ``conda list``

::

   (figshare_patrons) $ conda list requiam

You should see that the version is ``0.18.0``.

Configuration Settings
~~~~~~~~~~~~~~~~~~~~~~

Configuration settings are specified through the
:repo-main-file:`config/figshare.ini <config/figshare.ini>`
file. The most important settings to set are those populated with
``***override***``. However, for our scripts, these settings can be
specified using multi-character flag options, such as
``--ldap_password``. Note that most ``figshare.ini`` settings can be
overwritten through the command line.

For manual override (v0.11.0) where IAM portal and quota settings differ
from norm, ``config`` will include two CSV templates for portal and
quota to specify those changes.

Testing Installation
~~~~~~~~~~~~~~~~~~~~

To test the installation without performing any ``portal`` or ``quota``
query, execute the following command:

::

   (figshare_patrons) $ export password="insert_password"
   (figshare_patrons) $ export persist_path="/path/to/persistent/storage"
   (figshare_patrons) $ ./scripts/script_run --config config/figshare.ini \
                          --persistent_path $persist_path \
                          --ldap_password $password --grouper_password $password

Test command-line flags (``test`` and ``test_reverse``) are available to
test EDS query and Grouper synchronization (with the ``sync`` flag) by
executing the following :

::

   (figshare_patrons) $ ./scripts/script_run --test \
                          --config config/figshare.ini --persistent_path $persist_path \
                          --ldap_password $password --grouper_password $password --sync

Note that the above will add a test NetID account to the following
Grouper group: ``arizona.edu:dept:LBRY:figshare:test``

Without the ``sync`` flag, the above command line will perform a “dry
run”. It will indicate what Grouper updates will occur.

To undo this change, use the ``test_reverse`` flag:

::

   (figshare_patrons) $ ./scripts/script_run --test_reverse \
                          --config config/figshare.ini --persistent_path $persist_path \
                          --ldap_password $password --grouper_password $password --sync


.. _ldap3: https://ldap3.readthedocs.io/en/latest/
.. _numpy: https://numpy.org/doc/
.. _pandas: https://pandas.pydata.org/
.. _tabulate: https://github.com/astanin/python-tabulate
.. _requests: https://requests.readthedocs.io/en/master/
.. _Anaconda: https://www.anaconda.com/distribution/
