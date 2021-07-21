from logging import Logger
from os.path import join
from typing import Any, Dict, List, Optional, Union
import requests
import pandas as pd

from requests.exceptions import HTTPError

from .commons import figshare_stem, figshare_group
from .delta import Delta

from redata.commons.logger import log_stdout

# Administrative groups
from .manual_override import ManualOverride, update_entries

superadmins = figshare_group('GrouperSuperAdmins', '', production=True)
admins = figshare_group('GrouperAdmins', '', production=True)
managers = figshare_group('GrouperManagers', '', production=True)


class Grouper:
    """
    This class uses the Grouper API to retrieve and send metadata

    See `Main Grouper API documentation
    <https://spaces.at.internet2.edu/display/Grouper/Grouper+Web+Services>`_.

    :param grouper_host: Grouper hostname (e.g., grouper.iam.arizona.edu)
    :param grouper_base_path: Grouper base path that includes the API version
           (e.g., grouper-ws/servicesRest/json/v2_2_001)
    :param grouper_user: Grouper username
    :param grouper_password: Grouper password credential
    :param grouper_production: Bool to use production stem, ``figshare``.
           Otherwise stage stem is used, ``figtest``. Default: production

    :ivar grouper_host: Grouper hostname
    :ivar grouper_base_path: Grouper base path that includes the API version
    :ivar grouper_user: Grouper username
    :ivar grouper_password: Grouper password credential
    :ivar grouper_production: Bool to use production stem, ``figshare``.
           Otherwise stage stem is used, ``figtest``
    :ivar tuple grouper_auth: Grouper credential
    :ivar str endpoint: Grouper endpoint
    :ivar dict headers: HTTPS header information
    """

    def __init__(self, grouper_host: str, grouper_base_path: str,
                 grouper_user: str, grouper_password: str,
                 grouper_production: bool = False,
                 log: Optional[Logger] = None):

        if isinstance(log, type(None)):
            self.log = log_stdout()
        else:
            self.log = log

        self.grouper_host = grouper_host
        self.grouper_base_path = grouper_base_path
        self.grouper_user = grouper_user
        self.grouper_password = grouper_password
        self.grouper_production = grouper_production

        self.grouper_auth: tuple = (self.grouper_user, self.grouper_password)
        self.endpoint: str = f'https://{grouper_host}/{grouper_base_path}'
        self.headers: dict = {'Content-Type': 'text/x-json'}

    def url(self, endpoint: str) -> str:
        """
        Return full Grouper URL endpoint

        :param endpoint: The URL endpoint to append to ``self.endpoint``

        :return: Complete HTTPS URL
        """

        return join(self.endpoint, endpoint)

    def query(self, group: str) -> Dict[str, Any]:
        """
        Query Grouper for list of members in a group.

        :param group: Grouper full group path from
               :func:`requiam.commons.figshare_group`

        :return: Grouper metadata
        """

        endpoint = self.url(f"groups/{group}/members")

        rsp = requests.get(endpoint, auth=self.grouper_auth)

        grouper_query_dict = vars(self)

        # Append query specifics
        grouper_query_dict['grouper_members_url'] = endpoint
        grouper_query_dict['grouper_group'] = group

        if 'wsSubjects' in rsp.json()['WsGetMembersLiteResult']:
            grouper_query_dict['members'] = \
                {s['id'] for s in rsp.json()['WsGetMembersLiteResult']['wsSubjects']}
        else:
            grouper_query_dict['members'] = set([])

        return grouper_query_dict

    def get_group_list(self, group_type: str) -> Any:
        """
        Retrieve list of groups in a Grouper stem

        See `Grouper API "Get Groups"
        <https://spaces.at.internet2.edu/display/Grouper/Get+Groups>`_
        but with a different implementation using FIND_BY_STEM_NAME method

        :param group_type: Grouper stem.
               Options are: 'portal', 'quota', 'test', 'group_active', ''.
               Note: Some groups (e.g., 'group_active') do not exist for production
        :raises ValueError: If incorrect ``group_type``

        :return: JSON response
        """

        if group_type not in ['portal', 'quota', 'test', 'group_active', '']:
            raise ValueError("Incorrect [group_type] input")

        endpoint = self.url('groups')

        grouper_stem = figshare_stem(group_type,
                                     production=self.grouper_production)

        params = dict()
        params['WsRestFindGroupsRequest'] = {
            'wsQueryFilter':
                {'queryFilterType': 'FIND_BY_STEM_NAME',
                 'stemName': grouper_stem}
        }

        rsp = requests.post(endpoint, json=params, headers=self.headers,
                            auth=self.grouper_auth)

        return rsp.json()

    def get_group_details(self, group: str) -> Any:
        """
        Retrieve group details

        See `Grouper API "Get Groups"
        <https://spaces.at.internet2.edu/display/Grouper/Get+Groups>`_
        but using WsRestFindGroupsRequest

        :param group: Grouper path from :func:`requiam.commons.figshare_group`

        :return: JSON response
        """

        endpoint = self.url('groups')

        params = dict()
        params['WsRestFindGroupsRequest'] = {
            'wsQueryFilter':
                {'queryFilterType': 'FIND_BY_GROUP_NAME_APPROXIMATE',
                 'groupName': group}
        }

        rsp = requests.post(endpoint, json=params, headers=self.headers,
                            auth=self.grouper_auth)

        return rsp.json()['WsFindGroupsResults']['groupResults']

    def check_group_exists(self, group: str, group_type: str) -> bool:
        """
        Check whether a Grouper group exists within a Grouper stem

        See `Grouper API "Find Groups"
        <https://spaces.at.internet2.edu/display/Grouper/Find+Groups>`_

        :param group: Grouper full group path from
               :func:`requiam.commons.figshare_group`
        :param group_type: Grouper stem.
               Options are: 'portal', 'quota', 'test', 'group_active', ''

        :raises ValueError: If incorrect ``group_type``
        :raises KeyError: Stem does not exists
        """

        if group_type not in ['portal', 'quota', 'test', 'group_active', '']:
            raise ValueError("Incorrect [group_type] input")

        result = self.get_group_list(group_type)

        try:
            group_df = pd.DataFrame(result['WsFindGroupsResults']['groupResults'])

            df_query = group_df.loc[group_df['displayExtension'] == str(group)]

            status = True if not df_query.empty else False
            return status
        except KeyError:
            raise KeyError("Stem is empty")

    def add_group(self, group: str, group_type: str, description: str) \
            -> bool:
        """
        Create Grouper group within a Grouper stem

        See `Grouper API "Group Save"
        <https://spaces.at.internet2.edu/display/Grouper/Group+Save>`_

        :param group: Grouper full group path from
               :func:`requiam.commons.figshare_group`
        :param group_type: Grouper stem from
               :func:`requiam.commons.figshare_stem`.
               Options are: 'portal', 'quota', 'test', 'group_active', ''
        :param description: Description of group to include as metadata.
               This shows up in the Grouper UI

        :raises ValueError: If incorrect ``group_type``
        :raises HTTPError: If the Grouper POST fails with a non-200 status
        """

        endpoint = self.url("groups")

        if group_type not in ['portal', 'quota', 'test', 'group_active']:
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
                                   auth=self.grouper_auth)

            metadata = result.json()['WsGroupSaveResults']['resultMetadata']

            if metadata['resultCode'] == 'SUCCESS':
                return True
            else:
                errmsg = f"add_group - Error: {metadata['resultCode']}"
                raise errmsg
        except requests.exceptions.HTTPError:
            raise requests.exceptions.HTTPError

    def add_privilege(self,
                      access_group: str,
                      target_group: str, 
                      target_group_type: str,
                      privileges: Union[str, List[str]]) -> bool:
        """
        Add privilege(s) for a Grouper group to access target

        See `Grouper API "Add or remove Grouper privileges"
        <https://spaces.at.internet2.edu/display/Grouper/Add+or+remove+grouper+privileges>`_

        :param access_group: Grouper group to give access to,
               ex: arizona.edu:Dept:LBRY:figshare:GrouperSuperAdmins
        :param target_group: Grouper group to add privilege on, ex: "apitest"
        :param target_group_type: Grouper stem associated with the group to
               add privilege on, ex: use 'figtest' for
               'arizona.edu:Dept:LBRY:figtest:test'
        :param privileges: Grouper privileges. Allowed values:
               'read', 'view', 'update', 'admin', 'optin', 'optout'

        :raises ValueError: Incorrect ``privileges`` or Grouper POST failed
        :raises KeyError: Incorrect ``target_group_type``
        :raises Exception: Incorrect ``access_group`` (check for existence)

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
                                       auth=self.grouper_auth)
                metadata = result.json()['WsAssignGrouperPrivilegesLiteResult']['resultMetadata']

                if metadata['resultCode'] not in ['SUCCESS_ALLOWED', 'SUCCESS_ALLOWED_ALREADY_EXISTED']:
                    raise ValueError(f"Unexpected result received: {metadata['resultCode']}")

        return True


def create_groups(groups: Union[str, List[str]],
                  group_type: str,
                  group_descriptions: Union[str, List[str]],
                  grouper_api: Grouper,
                  log0: Optional[Logger] = None,
                  add: bool = False) -> None:
    """
    Process through a list of Grouper groups and add them if they don't exist
    and set permissions

    :param groups: List containing group names
    :param group_type: Grouper stem name. Either 'portal', 'quota', or 'test'
    :param group_descriptions: Descriptions of group to include as metadata.
           This shows up in the Grouper UI
    :param grouper_api: ``Grouper`` object
    :param log0: Logging object
    :param add: Indicate whether to perform update or dry run.
           Default: ``False``

    :raises HTTPError: Grouper POST fails
    """

    if isinstance(log0, type(None)):
        log0 = log_stdout()

    if isinstance(groups, str):
        groups = [groups]
    if isinstance(group_descriptions, str):
        group_descriptions = [group_descriptions]

    for group, description in zip(groups, group_descriptions):
        add_dict = {'group': group,
                    'group_type': group_type,
                    'description': description}

        # Check if group exists
        try:
            group_exists = grouper_api.check_group_exists(group, group_type)
        except KeyError:
            log0.info("Stem is empty")
            group_exists = False

        if not group_exists:
            log0.info(f"Group does not exist : {group}")

            if add:
                log0.info(f'Adding {group} ...')
                try:
                    add_result = grouper_api.add_group(**add_dict)
                    if add_result:
                        log0.info("SUCCESS")
                except HTTPError:
                    raise HTTPError
            else:
                log0.info('dry run, not performing group add')
        else:
            log0.info(f"Group exists : {group}")

        if add:
            log0.info(f'Adding admin privileges for groupersuperadmins ...')
            try:
                add_privilege = grouper_api.add_privilege(superadmins, group, group_type, 'admin')
                if add_privilege:
                    log0.info("SUCCESS")
            except HTTPError:
                raise HTTPError

            log0.info(f'Adding privileges for grouperadmins ...')
            try:
                add_privilege = grouper_api.add_privilege(admins, group, group_type,
                                                          ['read', 'view', 'optout'])
                if add_privilege:
                    log0.info("SUCCESS")
            except HTTPError:
                raise HTTPError

        else:
            log0.info('dry run, not performing privilege add')


def create_active_group(group: str,
                        grouper_dict: dict,
                        group_description: Optional[str] = None,
                        log: Optional[Logger] = None,
                        add: bool = False) -> None:
    """
    Create a temporary group for figshare:active indirect membership

    :param group: Name of group (e.g., "ual")
    :param grouper_dict: Grouper configuration settings
    :param group_description: Grouper description. Defaults will prompt for it
    :param log: Logging object
    :param add: Indicate adding group. Default: ``False`` (dry run)
    """

    if isinstance(log, type(None)):
        log = log_stdout()

    # This is for figtest stem
    ga_test = Grouper(**grouper_dict, grouper_production=False, log=log)

    if isinstance(group_description, type(None)):
        log.info("PROMPT: Provide description for group...")
        group_description = input("PROMPT: ")
        log.info(f"RESPONSE: {group_description}")

    create_groups(group, 'group_active', group_description, ga_test,
                  log0=log, add=add)


def grouper_delta_user(group: str,
                       stem: str,
                       netid: Union[str, List[str]],
                       uaid: Union[str, List[str]],
                       action: str,
                       grouper_dict: Dict[str, Any],
                       delta_dict: Dict[str, Any],
                       mo: Optional[ManualOverride] = None,
                       sync: bool = False,
                       log: Optional[Logger] = None,
                       production: bool = True) -> Delta:
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
    grouper = Grouper(**grouper_dict)
    grouper_query_dict = grouper.query(grouper_query)

    if not isinstance(netid, list):
        netid = [netid]
    if not isinstance(uaid, list):
        uaid = [uaid]
    member_set = update_entries(grouper_query_dict['members'],
                                netid, uaid, action, log=log)

    d = Delta(ldap_members=member_set,
              grouper_query_dict=grouper_query_dict,
              **delta_dict, log=log)

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
