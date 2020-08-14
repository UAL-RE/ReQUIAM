import requests
import pandas as pd

from .commons import figshare_stem
from .grouper_query import figshare_group


class GrouperAPI:
    """
    Purpose:
      This class uses the Grouper API to retrieve a variety of content

    Additional documentation forthcoming
    """

    def __init__(self, grouper_host, grouper_base_path, grouper_user, grouper_password):

        self.grouper_host = grouper_host
        self.grouper_base_dn = grouper_base_path
        self.grouper_user = grouper_user
        self.grouper_password = grouper_password

        self.endpoint = f'https://{grouper_host}/{grouper_base_path}'
        self.headers = {'Content-Type': 'text/x-json'}

    def url(self, endpoint):
        """Return URL endpoint"""

        return f"{self.endpoint}/{endpoint}"

    def get_group_list(self, group_type):
        """Retrieve list of groups in a Grouper stem"""

        if group_type not in ['portal', 'quota', '']:
            raise ValueError("Incorrect [group_type] input")

        grouper_group = figshare_stem(group_type)

        params = dict()
        params['WsRestFindGroupsRequest'] = {'wsQueryFilter':
                                                 {'queryFilterType': 'FIND_BY_STEM_NAME',
                                                  'stemName': grouper_group}}

        rsp = requests.post(self.endpoint, auth=(self.grouper_user, self.grouper_password),
                            json=params, headers=self.headers)

        return rsp.json()

    def check_group_exists(self, group, group_type):
        """Check whether a Grouper group exists within a Grouper stem"""

        if group_type not in ['portal', 'quota']:
            raise ValueError("Incorrect [group_type] input")

        result = self.get_group_list(group_type)

        group_df = pd.DataFrame(result['WsFindGroupsResults']['groupResults'])

        df_query = group_df.loc[group_df['displayExtension'] == group]
        status = True if not df_query.empty else False
        return status

    def add_group(self, group, group_type, display_name, description):
        """Create Grouper group within a Grouper stem"""

        endpoint = self.url("groups")

        if group_type not in ['portal', 'quota']:
            raise ValueError("Incorrect [group_type] input")

        grouper_name = figshare_group(group, group_type)

        params = dict()
        params['WsRestGroupSaveRequest'] = {
            'wsGroupToSaves': [
                {'wsGroup': {'description': description,
                             'displayExtension': display_name,
                             'name': grouper_name},
                 'wsGroupLookup': {'groupName': grouper_name}}
            ]
        }

        try:
            result = requests.post(endpoint, auth=(self.grouper_user, self.grouper_password),
                                   json=params, headers=self.headers)

            metadata = result['WsGroupSaveResults']['resultMetadata']

            if metadata['resultCode'] == 'SUCCESS':
                return True
            else:
                errmsg = f"add_group - Error: {metadata['resultCode']}"
                raise errmsg
        except requests.exceptions.HTTPError:
            raise requests.exceptions.HTTPError
