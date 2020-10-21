import requests

from os.path import join
from .delta import Delta
from .manual_override import update_entries
from .commons import figshare_stem
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


def figshare_group(group, root_stem, production=True):
    """
    Purpose:
      Construct Grouper figshare groups

    :param group: str or int of group name. Cannot be empty
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

    if not group:
        raise ValueError("WARNING: Empty [group]")

    stem_query = figshare_stem(stem=root_stem, production=production)

    grouper_group = f'{stem_query}:{group}'

    return grouper_group


def grouper_delta_user(group, stem, netid, uaid, action, grouper_dict,
                       delta_dict, mo=None, sync=False, log=None, production=True):
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
    :param mo: ManualOverride object
      For implementing change to CSV files. Default: None
    :param sync: bool
      Indicate whether to sync. Default: False
    :param log: LogClass object
      For logging
    :param production: Bool to use production stem. Otherwise a stage/test is used. Default: True

    :return d: Delta object class
    """

    if isinstance(log, type(None)):
        log = log_stdout()

    grouper_query = figshare_group(group, stem, production=production)
    gq = GrouperQuery(**grouper_dict, grouper_group=grouper_query)

    member_set = gq.members
    if not isinstance(netid, list):
        netid = [netid]
    if not isinstance(uaid, list):
        netid = [netid]
    member_set = update_entries(member_set, netid, uaid, action, log=log)

    d = Delta(ldap_members=member_set,
              grouper_query_instance=gq,
              **delta_dict,
              log=log)

    log.info(f"ldap and grouper have {len(d.common)} members in common")
    log.info(f"synchronization will drop {len(d.drops)} entries to Grouper {group} group")
    log.info(f"synchronization will add {len(d.adds)} entries to Grouper {group} group")

    if sync:
        log.info('synchronizing ...')
        d.synchronize()

        # Update manual CSV file
        if not isinstance(mo, type(None)):
            if production:
                mo.update_dataframe(netid, uaid, group, stem)
            else:
                log.info("Working with figtest stem. Not updating dataframe")
    else:
        log.info('dry run, not performing synchronization')
        log.info('dry run, not updating dataframe')

    return d
