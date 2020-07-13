import pandas as pd

from .ldap_query import LDAPConnection, uid_query
from .grouper_query import figshare_stem

class ManualOverride:
    """
    Purpose:
      This class handles manual override changes.  It reads in CSV
      configuration files and queries pandas DataFrame
      to identify additions and deletions. Employ set operations for
      simplicity

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

        # Read in as pandas DataFrame
        self.portal_df = self.read_manual_file(self.portal_file)
        self.quota_df = self.read_manual_file(self.quota_file)

    @staticmethod
    def read_manual_file(input_file):
        """Read in manual override file as pandas DataFrame"""

        try:
            df = pd.read_csv(input_file, comment='#')

            return df
        except FileNotFoundError:
            print(f"File not found! : {input_file}")

    @staticmethod
    def update_entries(ldap_set, netid, uaid, action):
        """Add/remove entries from a set"""

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
            add_ldap_set = self.update_entries(ldap_set, add_df['netid'],
                                               add_df['uaid'], 'add')

        # Identify those that needs to be excluded in [group]
        outside_df = manual_df.loc[manual_df[group_type] != group]
        if len(outside_df) > 0:
            new_ldap_set = self.update_entries(add_ldap_set, outside_df['netid'],
                                               outside_df['uaid'], 'remove')
        else:
            new_ldap_set = add_ldap_set

        return new_ldap_set

    @staticmethod
    def get_current_groups(uid, ldap_dict, log):
        """Retrieve current Figshare ismemberof association"""
        mo_ldc = LDAPConnection(**ldap_dict)
        mo_ldc.ldap_attribs = ['ismemberof']

        user_query = f'(uid={uid})'
        print(user_query)

        mo_ldc.ldc.search(mo_ldc.ldap_search_dn, user_query, attributes=mo_ldc.ldap_attribs)

        membership = mo_ldc.ldc.entries[0].ismemberof.value

        figshare_dict = dict()

        # Extract portal
        portal_stem = figshare_stem('portal')
        portal = [s for s in membership if ((portal_stem in s) and ('grouper' not in s))]
        if len(portal) == 0:
            log.info("No Grouper group found!")
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
        else:
            if len(quota) != 1:
                log.warning("ERROR! Multiple Grouper quota found")
                raise ValueError
            else:
                figshare_dict['quota'] = quota[0].replace(quota_stem + ':', '')
                log.info(f"Current quota is : {figshare_dict['quota']} bytes")

        return figshare_dict
