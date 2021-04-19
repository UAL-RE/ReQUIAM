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
    Purpose:
      This class handles manual override changes.  It reads in CSV
      configuration files and queries pandas DataFrame to identify additions
      and deletions. Employ set operations for simplicity. It also update
      the pandas DataFrame after a change is implemented

    Attributes
    ----------
    portal_file : str
      Full file path for CSV file containing manual portal specs (e.g., config/portal_manual.csv)
    quota_file : str
      Full file path for CSV file containing manual quota specs (e.g., config/quota_manual.csv)
    log : LogClass object
      For logging
    root_add: bool
      Flag to set root as portal in manual CSV file

    portal_df : pandas.core.frame.DataFrame
      pandas DataFrame of [portal_csv]
    quota_df : pandas.core.frame.DataFrame
      pandas DataFrame of [quota_csv]

    portal_header : list containing portal header (commented out text) of [portal_csv]
    quota_header : list containing quota header (commented out text) of [quota_csv]

    Methods
    -------
    file_checks(input_file):
      Checks to see if manual CSV file exists. If not return a False boolean

    read_manual_file(group_type):
      Return a pandas DataFrame containing the manual override file

    identify_changes(ldap_set, group, group_type):
      Identify changes to call update_entries accordingly

    update_dataframe(netid, uaid, group, group_type):
      Update pandas DataFrame with necessary changes
    """
    def __init__(self, portal_file, quota_file, log=None, root_add=False):
        if isinstance(log, type(None)):
            self.log = log_stdout()
        else:
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

    def file_checks(self, input_file):
        """Checks to see if manual CSV file exists. If not return a False boolean"""
        file_pass = True
        if not exists(input_file):
            self.log.info(f"File not found! {input_file}")
            file_pass = False

            if islink(input_file):
                self.log.info(f"{input_file} is symbolic link")
        return file_pass

    def read_manual_file(self, group_type):
        """Return a pandas DataFrame containing the manual override file"""

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

    def identify_changes(self, ldap_set, group, group_type):
        """Identify changes to call update_entries accordingly"""

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

    def update_dataframe(self, netid, uaid, group, group_type):
        """Update pandas DataFrame with necessary changes"""

        if group_type not in ['portal', 'quota']:
            raise ValueError("Incorrect [group_type] input")

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


def csv_commented_header(input_file):
    """
    Purpose:
      Read in the comment header in CSV files to re-populate later

    :param input_file: full filename

    :return: header: list of strings
    """

    f = open(input_file, 'r')
    f_all = f.readlines()
    header = [line for line in f_all if line.startswith('#')]

    f.close()
    return header


def update_entries(ldap_set, netid, uaid, action, log=None):
    """
    Purpose:
      Add/remove entries from a set

    :param ldap_set: set of uaid values
    :param netid: list. User netid
    :param uaid: list. User uaid
    :param action: str
      Action to perform. Either 'remove' or 'add'
    :param log: LogClass object
    :return new_ldap_set: Updated set of uaid values
    """

    if isinstance(log, type(None)):
        log = log_stdout()

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


def get_current_groups(uid, ldap_dict, production=False, log=None, verbose=True):
    """
    Purpose:
      Retrieve current Figshare ismemberof association

    :param uid: str containing User NetID
    :param ldap_dict: dict containing ldap settings
    :param production: bool flag to indicate using figshare over figtest
    :param log: LogClass object for logging
    :param verbose: bool flag to provide information about each user
    :return figshare_dict: dict containing current Figshare portal and quota
    """

    if isinstance(log, type(None)):
        log = log_stdout()

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
