from logging import Logger
import pandas as pd
from os.path import exists, join, islink, dirname

from .ldap_query import LDAPConnection
from .commons import figshare_stem
from redata.commons.logger import log_stdout

root_dir = dirname(dirname(__file__))
portal_template_file = join(root_dir, 'config/portal_manual_template.csv')
quota_template_file = join(root_dir, 'config/quota_manual_template.csv')


class ManualOverride:
    """
    This class handles manual override changes. It reads in CSV configuration
    files and queries ``pandas.DataFrame`` to identify additions/deletions.
    It employ set operations for simplicity. It also update the CSV files
    after a change is implemented

    :param portal_file: Full file path for CSV file containing manual portal
           specifications (e.g., config/portal_manual.csv)
    :param quota_file: Full file path for CSV file containing manual quota
           specifications (e.g., config/quota_manual.csv)
    :param log: File and/or stdout logging
    :param root_add: Flag to set root as portal in manual CSV file.
           Default: ``False``. In the default case, a force to "root" will
           delete existing records in the manual quota CSV. If user ID is not
           present, nothing happens

    :ivar str portal_file: Full file path for CSV file containing manual portal
          specification
    :ivar str quota_file: Full file path for CSV file containing manual quota
          specification
    :ivar Logger log: File and/or stdout logging
    :ivar pd.DataFrame portal_df: Portal DataFrame
    :ivar pd.DataFrame quota_df: Quota DataFrame
    :ivar list portal_header: CSV header for ``portal_df``
    :ivar list quota_header: CSV header for ``quota_df``
    """
    def __init__(self, portal_file: str, quota_file: str,
                 log: Logger = log_stdout(), root_add: bool = False) -> None:

        self.log = log

        # If files exist use, otherwise, use available templates
        if self.file_checks(portal_file):
            self.portal_file = portal_file
        else:
            self.portal_file = portal_template_file
            self.log.info(f"Using: {self.portal_file}")

        if self.file_checks(quota_file):
            self.quota_file = quota_file
        else:
            self.quota_file = quota_template_file
            self.log.info(f"Using: {self.quota_file}")

        # Read in CSV as pandas DataFrame
        self.portal_df = self.read_manual_file('portal')
        self.quota_df = self.read_manual_file('quota')

        # Read in CSV headers
        self.portal_header = csv_commented_header(self.portal_file)
        self.quota_header = csv_commented_header(self.quota_file)

        # This flag it to indicate whether root should be included for
        # portal association
        self.root_add = root_add

    def file_checks(self, input_file: str) -> bool:
        """
        Checks to see if manual CSV file exists.

        :param input_file: Path of file to check

        :return: Result of file check
        """

        file_pass = True
        if not exists(input_file):
            self.log.info(f"File not found! {input_file}")
            file_pass = False

            if islink(input_file):
                self.log.info(f"{input_file} is symbolic link")
        return file_pass

    def read_manual_file(self, group_type: str) -> pd.DataFrame:
        """
        Return a ``pandas.DataFrame`` containing the manual override file

        :param group_type: Grouper group type. Either 'portal' or 'quota'

        :raises ValueError: Incorrect input on ``group_type``
        :raises FileNotFound: Unable to find manual CSV to load

        :return: DataFrame corresponding to ``group_type``
        """

        if group_type not in ['portal', 'quota']:
            raise ValueError("Incorrect [group_type] input")

        if group_type == 'portal':
            input_file = self.portal_file
        if group_type == 'quota':
            input_file = self.quota_file

        dtype_dict = {'netid': str, 'uaid': str}

        if group_type == 'portal':
            dtype_dict[group_type] = str
        if group_type == 'quota':
            dtype_dict[group_type] = int

        try:
            df = pd.read_csv(input_file, comment='#', dtype=dtype_dict)

            return df
        except FileNotFoundError:
            self.log.info(f"File not found! : {input_file}")

    def identify_changes(self, ldap_set: set,
                         group: str, group_type: str) -> set:
        """
        Identify changes to call :func:`requiam.manual_override.update_entries`
        accordingly

        :param ldap_set: Input EDS user IDs
        :param group: Group to identify membership
        :param group_type: Manual CSV type. Either 'portal' or 'quota'

        :raises ValueError: Incorrect input on ``group_type``

        :return: EDS user IDs with changes (after addition and deletion)
        """

        if group_type not in ['portal', 'quota']:
            raise ValueError("Incorrect [group_type] input")

        manual_df = pd.DataFrame()
        if group_type == 'portal':
            manual_df = self.portal_df

        if group_type == 'quota':
            manual_df = self.quota_df

        # Identify those that needs be included in [group]
        add_df = manual_df.loc[manual_df[group_type] == group]

        add_ldap_set = set(ldap_set)
        if len(add_df) > 0:
            # Add to ldap_set
            add_netid = add_df['netid'].to_list()
            add_uaid = add_df['uaid'].to_list()
            add_ldap_set = update_entries(ldap_set, add_netid, add_uaid,
                                          'add', log=self.log)

        # Identify those that needs to be excluded in [group]
        outside_df = manual_df.loc[manual_df[group_type] != group]
        if len(outside_df) > 0:
            out_netid = outside_df['netid'].to_list()
            out_uaid = outside_df['uaid'].to_list()
            new_ldap_set = update_entries(add_ldap_set, out_netid, out_uaid,
                                          'remove', log=self.log)
        else:
            new_ldap_set = add_ldap_set

        return new_ldap_set

    def update_dataframe(self, netid: list, uaid: list,
                         group: str, group_type: str) -> None:
        """
        Update ``pandas.DataFrame`` with necessary changes

        :param netid: UA NetIDs
        :param uaid: UA IDs
        :param group: Group to identify membership
        :param group_type: Manual CSV type. Either 'portal' or 'quota'

        :raises ValueError: Incorrect input on ``group_type``
        """

        if group_type not in ['portal', 'quota']:
            raise ValueError("Incorrect [group_type] input")

        revised_df = pd.DataFrame()
        if group_type == 'portal':
            revised_df = self.portal_df
        if group_type == 'quota':
            revised_df = self.quota_df

        for i in range(len(netid)):
            loc0 = revised_df.loc[revised_df['netid'] == netid[i]].index

            table_update = True
            if group == 'root':
                if group_type == 'quota' or not self.root_add:
                    table_update = False

            if len(loc0) == 0:
                if table_update:
                    self.log.info(f"Adding entry for {netid[i]}")
                    revised_df.loc[len(revised_df)] = [netid[i], list(uaid)[i], group]
                else:
                    self.log.info(f"No update needed - root setting and {netid[i]} is not in list")
            else:
                if table_update:
                    self.log.info(f"Updating entry for {netid[i]}")
                    revised_df.loc[loc0[0]] = [netid[i], list(uaid)[i], group]
                else:
                    self.log.info(f"Removing entry for {netid[i]}")
                    revised_df = revised_df.drop(loc0)

        self.log.info(f"Updating {group_type} csv")
        if group_type == 'portal':
            self.portal_df = revised_df

            self.log.info(f"Overwriting : {self.portal_file}")
            f = open(self.portal_file, 'w')
            f.writelines(self.portal_header)
            self.portal_df.to_csv(f, index=False)

        if group_type == 'quota':
            self.quota_df = revised_df

            self.log.info(f"Overwriting : {self.quota_file}")
            f = open(self.quota_file, 'w')
            f.writelines(self.quota_header)
            self.quota_df.to_csv(f, index=False)


def csv_commented_header(input_file: str) -> list:
    """
    Read in the comment header in CSV file to re-populate later

    :param input_file: Full path to CSV file

    :return: CSV header
    """

    f = open(input_file, 'r')
    f_all = f.readlines()
    header = [line for line in f_all if line.startswith('#')]

    f.close()
    return header


def update_entries(ldap_set: set, netid: list, uaid: list, action: str,
                   log: Logger = log_stdout()) -> set:
    """
    Add/remove entries from a set

    :param ldap_set: UA IDs from EDS
    :param netid: UA NetIDs to add/remove
    :param uaid: UA IDs for corresponding ``netid``
    :param action: Action to perform. Either 'remove' or 'add'
    :param log: File and/or stdout ``Logger`` object

    :raises ValueError: Incorrect ``action`` setting

    :return: Updated set of ``uaid`` values
    """

    if action not in ['remove', 'add']:
        raise ValueError("Incorrect [action] input")

    new_ldap_set = set(ldap_set)

    if action == 'remove':
        remove_uaid = ldap_set & set(uaid)
        if len(remove_uaid) > 0:
            remove_netid = [netid[i] for i in range(len(netid)) if
                            uaid[i] in list(remove_uaid)]
            log.info(f"Removing : {', '.join(remove_netid)}")
        else:
            log.info("Nothing is removed")
        new_ldap_set = ldap_set - set(uaid)

    if action == 'add':
        new_uaid = set(uaid) - ldap_set
        if len(new_uaid) > 0:
            new_netid = [netid[i] for i in range(len(netid)) if
                         uaid[i] in list(new_uaid)]
            log.info(f"Adding : {', '.join(new_netid)}")
        else:
            log.info(f"Nothing is added")
        new_ldap_set = set.union(ldap_set, set(uaid))

    return new_ldap_set


def get_current_groups(uid: str, ldap_dict: dict, production: bool = False,
                       log: Logger = log_stdout(), verbose: bool = True) -> dict:
    """
    Retrieve current Figshare ``ismemberof`` association

    :param uid: User NetID
    :param ldap_dict: LDAP settings
    :param production: Flag to indicate using Grouper production stem
           (``figshare``) over test (``figtest``). Default: ``False``
    :param log: File and/or stdout logging
    :param verbose: Provide information about each user. Default: ``True``

    :raises ValueError: User is associated with multiple portal/quota groups

    :return figshare_dict: dict containing current Figshare portal and quota
    """

    mo_ldc = LDAPConnection(**ldap_dict)
    mo_ldc.ldap_attribs = ['ismemberof']

    user_query = f'(uid={uid})'

    mo_ldc.ldc.search(mo_ldc.ldap_search_dn, user_query, attributes=mo_ldc.ldap_attribs)

    membership = mo_ldc.ldc.entries[0].ismemberof.value

    figshare_dict = dict()

    revert_command = f'--netid {uid} '

    if isinstance(membership, type(None)):
        log.warning("No ismembersof attributes")

        figshare_dict['portal'] = 'root'
        figshare_dict['quota'] = 'root'
        figshare_dict['active'] = False

        revert_command += f'--active_remove --portal root --quota root '
        log.info(revert_command)
        return figshare_dict

    # Check for active group
    active_stem = figshare_stem('active', production=production)
    if active_stem in membership:
        figshare_dict['active'] = True
    else:
        log.warning(f"{uid} not member of {active_stem} group")
        figshare_dict['active'] = False

        revert_command += f'--active_remove '

    # Extract portal
    portal_stem = figshare_stem('portal', production=production)
    portal = [s for s in membership if ((portal_stem in s) and ('grouper' not in s))]
    if len(portal) == 0:
        log.info(f"No portal Grouper group found for {uid}!")
        figshare_dict['portal'] = 'root'  # Initialize to use later
    else:
        if len(portal) != 1:
            log.warning(f"ERROR! Multiple Grouper portal found for {uid}")
            raise ValueError
        else:
            figshare_dict['portal'] = portal[0].replace(portal_stem + ':', '')
            if verbose:
                log.info(f"Current portal is : {figshare_dict['portal']}")

    revert_command += f"--portal {figshare_dict['portal']} "

    # Extract quota
    quota_stem = figshare_stem('quota', production=production)
    quota = [s for s in membership if ((quota_stem in s) and ('grouper' not in s))]
    if len(quota) == 0:
        log.info(f"No quota Grouper group found for {uid}!")
        figshare_dict['quota'] = 'root'  # Initialize to use later
    else:
        if len(quota) != 1:
            log.warning(f"ERROR! Multiple Grouper quota found {uid}")
            raise ValueError
        else:
            figshare_dict['quota'] = quota[0].replace(quota_stem + ':', '')
            if verbose:
                log.info(f"Current quota is : {figshare_dict['quota']} bytes")

    revert_command += f"--quota {figshare_dict['quota']} "

    log.info(f"To revert, use: {revert_command}")
    return figshare_dict
