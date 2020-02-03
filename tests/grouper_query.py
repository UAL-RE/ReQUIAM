import requests


class GrouperQuery(object):
    """
    This class initializes an HTTP request to retrieve Grouper membership.
    This code was adapted from the following repository:
       https://github.com/ualibraries/patron-groups

    Quick how to:

    from DataRepository_patrons.tests import grouper_query
    grouper_host = 'grouper.iam.arizona.edu'
    grouper_base_path = 'grouper-ws/servicesRest/json/v2_2_001/groups'
    gq = GrouperQuery(grouper_host, grouper_base_path, USERNAME, PASSWORD, grouper_group)

    # You can retrieve the uaid via:
    members = gq.members
    """

    def __init__(self, grouper_host, grouper_base_path, grouper_user, grouper_password, grouper_group):

        self.grouper_host = grouper_host
        self.grouper_base_dn = grouper_base_path
        self.grouper_user = grouper_user
        self.grouper_password = grouper_password
        self.grouper_group = grouper_group

        self.grouper_group_members_url = 'https://{}/{}/{}/members'.format(grouper_host,
                                                                           grouper_base_path,
                                                                           grouper_group)

        rsp = requests.get(self.grouper_group_members_url, auth=(grouper_user, grouper_password))

        if 'wsSubjects' in rsp.json()['WsGetMembersLiteResult']:
            self._members = {s['id'] for s in rsp.json()['WsGetMembersLiteResult']['wsSubjects']}
        else:
            self._members = []

        return

    @property
    def members(self):
        return set(self._members)


def figshare_stem(stem):
    """
    Purpose:
      Construct Grouper figshare stems

    :param stem: string corresponding to the sub-stem
       Options are: 'quota', 'portal'

    :return stem_query: str
    """

    stem_query = 'arizona.edu:dept:LBRY:figshare:{}'.format(stem)
    return stem_query


def figshare_group(group, root_stem):
    """
    Purpose:
      Construct Grouper figshare groups

    :param group: str or int of group name
    :param root_stem: str of associated stem folder for [group]
    :return grouper_group: str containing full Grouper path

    Usage:
      For active group, call as: figshare_group('active', '')
        > 'arizona.edu:dept:LBRY:figshare:active'

      For a quota group, call as: figshare_group('2147483648', 'quota')
        > 'arizona.edu:dept:LBRY:figshare:quota:2147483648'

      For a portal group, call as: figshare_group('sci_math', 'portal')
        > 'arizona.edu:dept:LBRY:figshare:portal:sci_math'
    """

    stem_query = figshare_stem(root_stem)

    if root_stem == '':
        grouper_group = stem_query + group
    else:
        grouper_group = '{}:{}'.format(stem_query, group)

    return grouper_group
