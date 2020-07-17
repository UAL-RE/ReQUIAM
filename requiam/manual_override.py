import pandas as pd

from .ldap_query import LDAPConnection
from .commons import figshare_stem


class ManualOverride:
    """
    Purpose:
      This class handles manual override changes.  It reads in CSV
      configuration files and queries pandas DataFrame to identify additions
      and deletions. Employ set operations for simplicity. It also update
      the pandas DataFrame

    Attributes
    ----------
    portal_file : str
      Full file path for CSV file containing manual portal specifications (e.g., config/portal_manual.csv)
    quota_file : str
      Full file path for CSV file containing manual quota specifications (e.g., config/quota_manual.csv)

    portal_df : pandas.core.frame.DataFrame
      pandas DataFrame of [portal_csv]
    quota_df : pandas.core.frame.DataFrame
      pandas DataFrame of [quota_csv]

    Methods
    -------
    read_manual_file(input_file)
      Read in CSV file with pandas and return pandas DataFrame

    update_entries(ldap_set, netid, uaid, action)
      Add/remove (action="add"/"remove") entries from set (ldap_set) based on
      uaid input

    identify_changes(ldap_set, group, group_type):
      Primary function that identify necessary changes based on specified
      group (either a portal or quota)
    """
    def __init__(self, portal_file, quota_file):
        self.portal_file = portal_file
        self.quota_file = quota_file

        # Read in CSV as pandas DataFrame
        self.portal_df = read_manual_file(self.portal_file, 'portal')
        self.quota_df = read_manual_file(self.quota_file, 'quota')

        # Read in CSV headers
        self.portal_header = csv_commented_header(self.portal_file)
        self.quota_header = csv_commented_header(self.quota_file)

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
            add_ldap_set = update_entries(ldap_set, add_df['netid'],
                                          add_df['uaid'], 'add')

        # Identify those that needs to be excluded in [group]
        outside_df = manual_df.loc[manual_df[group_type] != group]
        if len(outside_df) > 0:
            new_ldap_set = update_entries(add_ldap_set, outside_df['netid'],
                                          outside_df['uaid'], 'remove')
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

        loc0 = revised_df.loc[revised_df['netid'] == netid].index
        if len(loc0) == 0:
            print(f"Adding entry for {netid}")
            revised_df.loc[len(revised_df)] = [netid, list(uaid)[0], group]
        else:
            print(f"Updating entry for {netid}")
            revised_df.loc[loc0[0]] = [netid, list(uaid)[0], group]

        print(f"Update {group_type} csv")
        if group_type == 'portal':
            self.portal_df = revised_df

            print(f"Overwriting : {self.portal_file}")
            f = open(self.portal_file, 'w')
            f.writelines(self.portal_header)
            self.portal_df.to_csv(f, index=False)

        if group_type == 'quota':
            self.quota_df = revised_df

            print(f"Overwriting : {self.quota_file}")
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


def read_manual_file(input_file, group_type):
    """
    Purpose:
      Read in manual override file as pandas DataFrame

    :param input_file: full filename
    :param group_type: str containing group_type. Either 'portal' or 'quota'
    :return df: pandas DataFrame
    """

    if group_type not in ['portal', 'quota']:
        raise ValueError("Incorrect [group_type] input")

    dtype_dict = {'netid': str, 'uaid': str}

    if group_type == 'portal':
        dtype_dict[group_type] = str
    if group_type == 'quota':
        dtype_dict[group_type] = int

    try:
        df = pd.read_csv(input_file, comment='#', dtype=dtype_dict)

        return df
    except FileNotFoundError:
        print(f"File not found! : {input_file}")


def update_entries(ldap_set, netid, uaid, action):
    """
    Purpose:
      Add/remove entries from a set

    :param ldap_set: set of uaid values
    :param netid: User netid
    :param uaid: User uaid
    :param action: str
      Action to perform. Either 'remove' or 'add'
    :return new_ldap_set: Updated set of uaid values
    """

    if action not in ['remove', 'add']:
        raise ValueError("Incorrect [action] input")

    new_ldap_set = set(ldap_set)

    if action == 'remove':
        if isinstance(netid, list):
            print(f"Removing : {list(netid)}")
        if isinstance(netid, str):
            print(f"Removing : {netid}")
        new_ldap_set = ldap_set - uaid

    if action == 'add':
        if isinstance(netid, list):
            print(f"Adding : {list(netid)}")
        if isinstance(netid, str):
            print(f"Adding : {netid}")
        new_ldap_set = set.union(ldap_set, uaid)

    return new_ldap_set


def get_current_groups(uid, ldap_dict, log):
    """
    Purpose:
      Retrieve current Figshare ismemberof association

    :param uid: str containing User NetID
    :param ldap_dict: dict containing ldap settings
    :param log: LogClass object for logging
    :return figshare_dict: dict containing current Figshare portal and quota
    """

    mo_ldc = LDAPConnection(**ldap_dict)
    mo_ldc.ldap_attribs = ['ismemberof']

    user_query = f'(uid={uid})'

    mo_ldc.ldc.search(mo_ldc.ldap_search_dn, user_query, attributes=mo_ldc.ldap_attribs)

    membership = mo_ldc.ldc.entries[0].ismemberof.value

    figshare_dict = dict()

    if isinstance(membership, type(None)):
        log.warning("No ismembersof attributes")

        figshare_dict['portal'] = ''
        figshare_dict['quota'] = ''
        return figshare_dict

    # Extract portal
    portal_stem = figshare_stem('portal')
    portal = [s for s in membership if ((portal_stem in s) and ('grouper' not in s))]
    if len(portal) == 0:
        log.info("No Grouper group found!")
        figshare_dict['portal'] = ''  # Initialize to use later
    else:
        if len(portal) != 1:
            log.warning("ERROR! Multiple Grouper portal found")
            raise ValueError
        else:
            figshare_dict['portal'] = portal[0].replace(portal_stem + ':', '')
            log.info(f"Current portal is : {figshare_dict['portal']}")

    # Extract quota
    quota_stem = figshare_stem('quota')
    quota = [s for s in membership if ((quota_stem in s) and ('grouper' not in s))]
    if len(quota) == 0:
        log.info("No Grouper group found!")
        figshare_dict['quota'] = ''  # Initialize to use later
    else:
        if len(quota) != 1:
            log.warning("ERROR! Multiple Grouper quota found")
            raise ValueError
        else:
            figshare_dict['quota'] = quota[0].replace(quota_stem + ':', '')
            log.info(f"Current quota is : {figshare_dict['quota']} bytes")

    return figshare_dict
