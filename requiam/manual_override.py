import pandas as pd


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
            print(f"Removing : {list(netid)}")
            new_ldap_set = ldap_set - uaid

        if action == 'add':
            print(f"Adding : {list(netid)}")
            new_ldap_set = ldap_set + uaid

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
