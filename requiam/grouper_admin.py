from os.path import dirname, join
import requests
import pandas as pd

from .commons import figshare_stem
from .grouper_query import figshare_group

from .logger import log_stdout


class GrouperAPI:
    """
    Purpose:
      This class uses the Grouper API to retrieve and post a variety of
      Grouper content

      Main Grouper API doc:
        https://spaces.at.internet2.edu/display/Grouper/Grouper+Web+Services

    :param grouper_host: The grouper hostname (e.g., grouper.iam.arizona.edu)
    :param grouper_base_path: The grouper base path that includes the API version
                              (e.g., grouper-ws/servicesRest/json/v2_2_001)
    :param grouper_user: grouper username
    :param grouper_password: password credential
    :param grouper_production: bool to indicate whether to use production (figshare)
                               or stage (figtest) stem

    Attributes
    ----------
    grouper_host: str
    grouper_base_dn: str
    grouper_user: str
    grouper_password: str
    grouper_production: bool

    endpoint: str
      Grouper endpoint
    headers: dict
      HTTP header information

    Methods
    -------
    url(endpoint)
      Return full Grouper URL endpoint

    get_group_list(group_type)
      Retrieve list of groups in a Grouper stem
      group_type must be 'portal', 'quota', 'test' or ''

      See: https://spaces.at.internet2.edu/display/Grouper/Get+Groups
        but with a different implementation using the stem find

    get_group_details(group)
      Retrieve group details
      group must be the full Grouper path

      See: https://spaces.at.internet2.edu/display/Grouper/Get+Groups
        but using WsRestFindGroupsRequest

    check_group_exists(group, group_type)
      Check whether a Grouper group exists within a Grouper stem
      group_type must be 'portal', 'quota', 'test' or ''
      group is simply the group name

      See: https://spaces.at.internet2.edu/display/Grouper/Find+Groups

    add_group(group, group_type, description)
      Create Grouper group within a Grouper stem
      group_type must be 'portal', 'quota', or 'test'

      See: https://spaces.at.internet2.edu/display/Grouper/Group+Save

    add_privilege(access_group, target_group, target_group_type, privileges)
      Add privilege(s) for a Grouper group to access target

      See: https://spaces.at.internet2.edu/display/Grouper/Add+or+remove+grouper+privileges
    """

    def __init__(self, grouper_host, grouper_base_path, grouper_user,
                 grouper_password, grouper_production=False, log=None):

        if isinstance(log, type(None)):
            self.log = log_stdout()
        else:
            self.log = log

        self.grouper_host = grouper_host
        self.grouper_base_dn = grouper_base_path
        self.grouper_user = grouper_user
        self.grouper_password = grouper_password
        self.grouper_production = grouper_production

        self.endpoint = f'https://{grouper_host}/{grouper_base_path}'
        self.headers = {'Content-Type': 'text/x-json'}

    def url(self, endpoint):
        """Return full Grouper URL endpoint"""

        return join(self.endpoint, endpoint)

    def get_group_list(self, group_type):
        """Retrieve list of groups in a Grouper stem"""

        if group_type not in ['portal', 'quota', 'test', '']:
            raise ValueError("Incorrect [group_type] input")

        endpoint = self.url('groups')

        grouper_stem = figshare_stem(group_type, production=self.grouper_production)

        params = dict()
        params['WsRestFindGroupsRequest'] = {
            'wsQueryFilter':
                {'queryFilterType': 'FIND_BY_STEM_NAME',
                 'stemName': grouper_stem}
        }

        rsp = requests.post(endpoint, json=params, headers=self.headers,
                            auth=(self.grouper_user, self.grouper_password))

        return rsp.json()

    def get_group_details(self, group):
        """Retrieve group details. The full path is needed"""

        endpoint = self.url('groups')

        params = dict()
        params['WsRestFindGroupsRequest'] = {
            'wsQueryFilter':
                {'queryFilterType': 'FIND_BY_GROUP_NAME_APPROXIMATE',
                 'groupName': group}
        }

        rsp = requests.post(endpoint, json=params, headers=self.headers,
                            auth=(self.grouper_user, self.grouper_password))

        return rsp.json()['WsFindGroupsResults']['groupResults']

    def check_group_exists(self, group, group_type):
        """Check whether a Grouper group exists within a Grouper stem"""

        if group_type not in ['portal', 'quota', 'test', '']:
            raise ValueError("Incorrect [group_type] input")

        result = self.get_group_list(group_type)

        try:
            group_df = pd.DataFrame(result['WsFindGroupsResults']['groupResults'])

            df_query = group_df.loc[group_df['displayExtension'] == group]

            status = True if not df_query.empty else False
            return status
        except KeyError:
            raise KeyError("Stem is empty")

    def add_group(self, group, group_type, description):
        """Create Grouper group within a Grouper stem"""

        endpoint = self.url("groups")

        if group_type not in ['portal', 'quota', 'test']:
            raise ValueError("Incorrect [group_type] input")

        grouper_name = figshare_group(group, group_type,
                                      production=self.grouper_production)

        params = dict()
        params['WsRestGroupSaveRequest'] = {
            'wsGroupToSaves': [
                {'wsGroup': {'description': description,
                             'displayExtension': group,
                             'name': grouper_name},
                 'wsGroupLookup': {'groupName': grouper_name}}
            ]
        }

        try:
            result = requests.post(endpoint, json=params, headers=self.headers,
                                   auth=(self.grouper_user, self.grouper_password))

            metadata = result.json()['WsGroupSaveResults']['resultMetadata']

            if metadata['resultCode'] == 'SUCCESS':
                return True
            else:
                errmsg = f"add_group - Error: {metadata['resultCode']}"
                raise errmsg
        except requests.exceptions.HTTPError:
            raise requests.exceptions.HTTPError

    def add_privilege(self, access_group, target_group, target_group_type, privileges):
        """
        Purpose:
          Add privilege(s) for a Grouper group to access target

        :param access_group: name of group to give access to,
                             ex: arizona.edu:Dept:LBRY:figshare:GrouperSuperAdmins
        :param target_group: name of group to add privilege on, ex: "apitest"
        :param target_group_type: name of stem associated with the group to add privilege on,
                            ex: use 'test' for arizona.edu:Dept:LBRY:figtest:test
        :param privileges: single string, or list of strings of allowed values:
                           'read', 'view', 'update', 'admin', 'optin', 'optout'

        :return: True on success, otherwise raises an Exception
        """

        endpoint = self.url('grouperPrivileges')

        # Check privileges
        if isinstance(privileges, str):
            privileges = [privileges]
        for privilege in privileges:
            if privilege not in ['read', 'view', 'update', 'admin', 'optin', 'optout']:
                raise ValueError(f"Invalid privilege name: {privilege}")

        target_groupname = figshare_group(target_group, target_group_type,
                                          production=self.grouper_production)

        try:
            group_exists = self.check_group_exists(target_group, target_group_type)
        except KeyError:
            raise KeyError("ERROR: Stem is empty")

        if group_exists:
            args = self.get_group_details(access_group)
            if len(args):
                access_group_detail = args.pop()
            else:
                raise Exception(f"Could NOT find access_group: {access_group}")

            # initialize
            params = dict()
            params['WsRestAssignGrouperPrivilegesLiteRequest'] = {
                'allowed': 'T',
                'subjectId': access_group_detail['uuid'],
                'privilegeName': '',
                'groupName': target_groupname,
                'privilegeType': 'access'
            }

            for privilege in privileges:
                params['WsRestAssignGrouperPrivilegesLiteRequest']['privilegeName'] = privilege
                result = requests.post(endpoint, json=params, headers=self.headers,
                                       auth=(self.grouper_user, self.grouper_password))
                metadata = result.json()['WsAssignGrouperPrivilegesLiteResult']['resultMetadata']

                if metadata['resultCode'] not in ['SUCCESS_ALLOWED', 'SUCCESS_ALLOWED_ALREADY_EXISTED']:
                    raise ValueError(f"Unexpected result received: {metadata['resultCode']}")

        return True
