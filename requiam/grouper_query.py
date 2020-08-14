import requests

from .delta import Delta
from .manual_override import update_entries
from .commons import figshare_stem


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


def figshare_group(group, root_stem, production=True):
    """
    Purpose:
      Construct Grouper figshare groups

    :param group: str or int of group name
    :param root_stem: str of associated stem folder for [group]
    :param production: Bool to use production stem. Otherwise a stage/test is used. Default: True

    :return grouper_group: str containing full Grouper path

    Usage:
      For active group, call as: figshare_group('active', '')
        > 'arizona.edu:dept:LBRY:figshare:active'

      For a quota group, call as: figshare_group('2147483648', 'quota')
        > 'arizona.edu:dept:LBRY:figshare:quota:2147483648'
      Note: group can be specified as an integer for quota cases

      For a portal group, call as: figshare_group('sci_math', 'portal')
        > 'arizona.edu:dept:LBRY:figshare:portal:sci_math'
    """

    stem_query = figshare_stem(root_stem, production=production)

    if root_stem == '':
        grouper_group = stem_query + group
    else:
        grouper_group = '{}:{}'.format(stem_query, group)

    return grouper_group


def grouper_delta_user(group, stem, netid, uaid, action,
                       grouper_dict, delta_dict, log):
    """
    Purpose:
      Construct a Delta object for addition/deletion based for a specified
      user. This is designed primarily for the user_update script

    :param group: str
      The Grouper group to update
    :param stem: str
      The Grouper stem (e.g., 'portal', 'quota')
    :param netid: str
      The User NetID
    :param uaid: str
      The User UA ID
    :param action: str
      The action to perform. 'add' or 'remove'
    :param grouper_dict: dict
      Dictionary containing grouper settings
    :param delta_dict:
      Dictionary containing delta settings
    :param log: LogClass object
      For logging
    :return d: Delta object class
    """

    grouper_query = figshare_group(group, stem)
    gq = GrouperQuery(**grouper_dict, grouper_group=grouper_query)

    member_set = gq.members
    member_set = update_entries(member_set, netid, uaid, action, log)

    d = Delta(ldap_members=member_set,
              grouper_query_instance=gq,
              **delta_dict,
              log=log)

    log.info(f"ldap and grouper have {len(d.common)} members in common")
    log.info(f"synchronization will drop {len(d.drops)} entries to Grouper {group} group")
    log.info(f"synchronization will add {len(d.adds)} entries to Grouper {group} group")

    return d
