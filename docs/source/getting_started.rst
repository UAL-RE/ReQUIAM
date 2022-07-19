Getting Started
===============

These instructions will have the code running on your local or virtual
machine.

Requirements
~~~~~~~~~~~~

The :repo-main-file:`requirements.txt <requirements.txt>` indicates the required python
libraries. In short, you will need the following to have a working copy of
this software.


1. Python (>=3.8) (we use 3.9)
2. `ldap3`_ (2.6.1)
3. `numpy`_ (>=1.22.0) (we use 1.23.0)
4. :ual-re:`redata <redata-commons>` (>=0.5.0)
5. `pandas`_ (>=1.4.3)
6. `tabulate`_ (>=0.8.7) (we use 0.8.10)

7. `requests`_ (2.25.1)

Note: Python 3.7 will not be supported by Numpy 1.22.0 (June 2022). see https://github.com/UAL-RE/ReQUIAM/issues/170

Installation Instructions
~~~~~~~~~~~~~~~~~~~~~~~~~

Python and setting up a ``conda`` environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, we recommend using the `Anaconda`_ package installer the latest version under your account, which uses Python 3.9. We do not recommend to 
install it using `root`.


After that, you shall create a separate ``conda`` environment and activate it for ReQUIAM:

::

   $ conda create -n admin1 python=3.9
   $ conda activate admin1

Next, clone this repository into a parent folder:

::

   (admin1) $ cd /path/to/parent/folder
   (admin1) $ git clone https://github.com/UAL-RE/ReQUIAM.git

With the activated ``conda`` environment, you can install with the
``setup.py`` script:

::

   (admin1) $ cd /path/to/parent/folder/ReQUIAM
   (admin1) $ python setup.py develop

This will automatically installed the required ``pandas``, ``ldap3``,
``requests``, and ``numpy`` packages.

You can confirm installation via ``conda list``

::


   (admin1) $ conda list

You shall see the above packages versions matching the requirements.

For old version of redata (<0.5.0) and ReQUIAM, it might be easier to create a new conda user and follow the above steps.
Note: You can upgrade to Python 3.9 and related packages (numpy, pandas, and redata) from 3.7, but it takes more effort. 

::

   (admin1) $ conda list requiam

You should see that the version is ``1.1.0``.

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

   (admin1) $ export password="insert_password"
   (admin1) $ export persist_path="/path/to/persistent/storage"
   (admin1) $ ./scripts/script_run --config config/figshare.ini \
                          --persistent_path $persist_path \
                          --ldap_password $password --grouper_password $password


Test command-line flags (``test`` and ``test_reverse``) are available to
test EDS query and Grouper synchronization (with the ``sync`` flag) by
executing the following :

::

   (admin1) $ ./scripts/script_run --test \
                          --config config/figshare.ini --persistent_path $persist_path \
                          --ldap_password $password --grouper_password $password --sync

Note that the above will add a test NetID account to the following
Grouper group: ``arizona.edu:dept:LBRY:figshare:test``

Without the ``sync`` flag, the above command line will perform a “dry
run”. It will indicate what Grouper updates will occur.

To undo this change, use the ``test_reverse`` flag:

::

   (admin1) $ ./scripts/script_run --test_reverse \
                          --config config/figshare.ini --persistent_path $persist_path \
                          --ldap_password $password --grouper_password $password --sync


.. _ldap3: https://ldap3.readthedocs.io/en/latest/
.. _numpy: https://numpy.org/doc/
.. _pandas: https://pandas.pydata.org/
.. _tabulate: https://github.com/astanin/python-tabulate
.. _requests: https://requests.readthedocs.io/en/master/
.. _Anaconda: https://www.anaconda.com/distribution/
