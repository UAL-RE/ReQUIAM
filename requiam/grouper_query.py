import requests

from os.path import join
from .logger import log_stdout


class GrouperQuery(object):
    """
    Purpose:
      This class initializes an HTTP request to retrieve Grouper membership.
      This code was adapted from the following repository:
         https://github.com/ualibraries/patron-groups

    Usage:
      Quick how to:
        from requiam import grouper_query
        grouper_host = 'grouper.iam.arizona.edu'
        grouper_base_path = 'grouper-ws/servicesRest/json/v2_2_001/groups'
        grouper_group = 'arizona.edu:dept:LBRY:figshare:portal:sci_math'
        gq = grouper_query.GrouperQuery(grouper_host, grouper_base_path,
                                        USERNAME, PASSWORD, grouper_group)

      You can retrieve the EDS uid via:
        members = gq.members
    """

    def __init__(self, grouper_host, grouper_base_path, grouper_user,
                 grouper_password, grouper_group, log=None):

        if isinstance(log, type(None)):
            self.log = log_stdout()
        else:
            self.log = log

        self.grouper_host = grouper_host
        self.grouper_base_dn = grouper_base_path
        self.grouper_user = grouper_user
        self.grouper_password = grouper_password
        self.grouper_group = grouper_group

        self.endpoint = f'https://{grouper_host}/{grouper_base_path}'

        self.grouper_group_members_url = join(self.endpoint,
                                              f'groups/{grouper_group}/members')

        rsp = requests.get(self.grouper_group_members_url, auth=(grouper_user, grouper_password))

        if 'wsSubjects' in rsp.json()['WsGetMembersLiteResult']:
            self._members = {s['id'] for s in rsp.json()['WsGetMembersLiteResult']['wsSubjects']}
        else:
            self._members = []

        return

    @property
    def members(self):
        return set(self._members)
