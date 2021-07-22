Execution
=========

To execute the script and update Grouper and EDS, include the
``portal``, ``quota``, and ``sync`` command-line flags:

::

   (figshare_patrons) $ ./scripts/script_run --config config/figshare.ini \
                          --persistent_path $persist_path \
                          --ldap_password $password --grouper_password $password \
                          --quota --portal --sync

Note: Without the ``sync`` flag, the above command line will perform a
“dry run” where both ``quota`` and ``portal`` queries are conducted. It
will indicate what Grouper updates will occur.

By default, changes occur on the ``figshare`` stem. Execution can occur
on the ``figtest`` stem with the ``--grouper_figtest`` boolean flag.

There are additional options to run a subset of portals or organization
codes. This is specified with the ``--org_codes`` or ``--groups``
options, which accepts comma-separated inputs. For this to work, the
``--portal`` must be set. If ``--quota`` is specified, those users are
added to the appropriate group. Note that with this option, it will
create and populate a ``figtest:group_active`` group that allows for
indirect membership association. There are a couple of interactive
prompts to create the ``figtest:group_active`` group or provide an
existing one to use/update.


Manual Changes
~~~~~~~~~~~~~~

While the primary use of this software is automated updates through Grouper,
there are additional scripts for handling. One of those pertains to overriding
default changes (e.g., a user’s quota, involvement with a specific portal).
To this end, the ``user_update`` script should be used. It has several
features:

1. It can add a number of users to a specific group and also remove them from
   its previous group assignment(s)
2. It will update the appropriate CSV files. This ensures that the changes
   stay when the automated script ``script_run`` is executed
3. It has the ability to move a user to the “main” or “root” portal
4. It has a number of built-in error handling to identify possible input
   error. This includes:

   - A username that is not valid
   - A Grouper group that does not exist
   - Prevent any action if the user belongs to the specified group

Execution can be done as follows:

::

   (figshare_patrons) $ ./scripts/user_update --config config/figshare.ini \
                          --persistent_path $persist_path \
                          --ldap_password $password --grouper_password $password \
                          --quota 123456 --portal testportal --netid <username> --sync

Here, the script will update the specified ``<username>`` to be
associated with the ``123456`` quota and the ``testportal`` portal. Much
like ``script_run``, execution requires the ``--sync`` flag. Otherwise,
a list of changes will be provided. Note: ``<username>`` can be a list
of comma-separated users (e.g., ``user1,user2,user3``) or a .txt file
with each username on a new line.

::

   user1
   user2
   user3

To remove a user from its current assignment and place it on the main portal,
use: ``--portal root``. For quota, the ``root`` option will remove any quota
association (this is equivalent to a zero quota)

The manual CSV files are specified in the config file:

::

   # Manual override files
   portal_file = config/portal_manual.csv
   quota_file = config/quota_manual.csv

These settings, much like other settings (see ``python requiam/user_update --help``),
can be overwritten on the command line:

::

   --portal_file /path/to/portal_manual.csv
   --quota_file /path/to/quota_manual.csv

Note that working templates are provided in the config folder for
:repo-main-file:`quota <config/quota_manual_template.csv>` and
:repo-main-file:`portal <config/portal_manual_template.csv>`.

To disable updating the the manual CSV files, you can include the
following flags:
``--portal_file_noupdate --quota_file_noupdate``

By default, changes occur on the ``figshare`` stem. Execution can occur
on the ``figtest`` stem with the ``--grouper_figtest`` boolean flag.


API Management of Grouper Groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``add_grouper_groups`` currently create and assign privileges to groups
through the Grouper API. It uses the :ual-re:`ReQUIAM_csv <ReQUIAM_csv>`'s
`CSV file`_ for research themes and sub-portals. In addition, another
`Quota Google Sheet`_ exists for the quotas. The script will check whether
a group exists. If the ``add`` flag is provided, it will create the group and
assign privileges for GrouperSuperAdmins and GrouperAdmins. If a group already
exists, it will skip to the privilege assignments. To execute the script:

::

   (figshare_patrons) $ ./scripts/add_grouper_groups --config config/figshare.ini \
                          --persistent_path $persist_path --grouper_password $password \
                          --main_themes --sub_portals --quota --add

The ``main_themes``, ``sub_portals`` and ``quota`` flags will conduct
checks and create those sets of groups. Without the ``add`` flag, it is
a dry run. By default this works on a testing Grouper stem ``figtest``.
Set the ``production`` flag to implement on the production stem,
``figshare``.

.. _CSV file: https://raw.githubusercontent.com/UAL-RE/ReQUIAM_csv/master/requiam_csv/data/research_themes.csv
.. _Quota Google Sheet: https://docs.google.com/spreadsheets/d/12Rhfpz4aWIcOGOOu0Ev4sZNMiXvLr3FSl_83yRd3h4k/edit?usp=sharing