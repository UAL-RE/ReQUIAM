import datetime
import json
from logging import Logger
import requests
import time
from typing import Any, Dict, Optional

from .logger import log_stdout


class Delta:
    """
    Purpose:
      This class compares results from an LDAP query and a Grouper query
      to identify common, additions, and deletions so that the two
      will be in sync.

      This code was adapted from the following repository:
         https://github.com/ualibraries/patron-groups

    Usage:
      Quick how to:
        from requiam import delta

    """

    def __init__(self, ldap_members: set, grouper_query_dict: Dict[str, Any],
                 batch_size: int, batch_timeout: int, batch_delay: int,
                 sync_max: int, log: Optional[Logger] = None) -> None:

        if isinstance(log, type(None)):
            self.log = log_stdout()
        else:
            self.log = log

        self.log.debug('entered')

        self.ldap_members: set = ldap_members
        self.grouper_query_dict: Dict[str, Any] = grouper_query_dict
        self.grouper_members: set = grouper_query_dict['members']
        self.batch_size: int = batch_size
        self.batch_timeout: int = batch_timeout
        self.batch_delay: int = batch_delay
        self.sync_max: int = sync_max

        self.drops = self._drops()
        self.adds = self._adds()
        self.common = self._common()

        self.log.debug('returning')
        return

    def _common(self) -> set:
        common = self.ldap_members & self.grouper_members

        self.log.debug('finished common')
        return common

    def _adds(self) -> set:
        adds = self.ldap_members - self.grouper_members

        self.log.debug('finished adds')
        return adds

    def _drops(self) -> set:
        drops = self.grouper_members - self.ldap_members

        self.log.debug('finished drops')
        return drops

    def synchronize(self) -> None:
        self.log.debug('entered')

        total_delta = len(list(self.adds)) + len(list(self.drops))
        if total_delta > self.sync_max:
            self.log.warning(f"total delta ({total_delta}) exceeds maximum " +
                             f"sync limit ({self.sync_max}), will not synchronize")
            self.log.debug('finished synchronize')
            return

        self.log.info("synchronizing ldap query results to " +
                      f"{self.grouper_query_dict['grouper_group']}")
        self.log.info(f"batch size = {self.batch_size}, " +
                      f"batch timeout = {self.batch_timeout} seconds, " +
                      f"batch delay = {self.batch_delay} seconds")

        self.log.info('processing drops:')
        n_batches = 0
        list_of_drops = list(self.drops)
        for batch in [list_of_drops[i:i + self.batch_size] for
                      i in range(0, len(list_of_drops), self.batch_size)]:
            n_batches += 1

            start_t = datetime.datetime.now()
            rsp = requests.post(self.grouper_query_dict['grouper_members_url'],
                                auth=(self.grouper_query_dict['grouper_user'],
                                      self.grouper_query_dict['grouper_password']),
                                data=json.dumps({
                                    'WsRestDeleteMemberRequest': {
                                        'replaceAllExisting': 'F',
                                        'subjectLookups': [{'subjectId': entry} for entry in batch]
                                    }
                                }),
                                headers={'Content-type': 'text/x-json'},
                                timeout=self.batch_timeout)
            end_t = datetime.datetime.now()
            batch_t = (end_t - start_t).total_seconds()

            rsp_j = rsp.json()
            if rsp_j['WsDeleteMemberResults']['resultMetadata']['resultCode'] not in 'SUCCESS':
                self.log.warning('problem running batch delete, result code = %s',
                                 rsp_j['WsDeleteMemberResults']['resultMetadata']['resultCode'])
            else:
                self.log.info(f"dropped batch {n_batches}, " +
                              f"{len(batch)} entries, " +
                              f"{batch_t} seconds")

            if self.batch_delay > 0:
                self.log.info(f"pausing for {self.batch_delay} seconds")
                time.sleep(self.batch_delay)

        self.log.info('processing adds:')
        n_batches = 0
        list_of_adds = list(self.adds)
        for batch in [list_of_adds[i:i + self.batch_size] for
                      i in range(0, len(list_of_adds), self.batch_size)]:
            n_batches += 1

            start_t = datetime.datetime.now()
            rsp = requests.put(self.grouper_query_dict['grouper_members_url'],
                               auth=(self.grouper_query_dict['grouper_user'],
                                     self.grouper_query_dict['grouper_password']),
                               data=json.dumps({
                                   'WsRestAddMemberRequest': {
                                       'replaceAllExisting': 'F',
                                       'subjectLookups': [{'subjectId': entry} for entry in batch]
                                   }
                               }),
                               headers={'Content-type': 'text/x-json'},
                               timeout=self.batch_timeout)
            end_t = datetime.datetime.now()
            batch_t = (end_t - start_t).total_seconds()

            rsp_j = rsp.json()
            if rsp_j['WsAddMemberResults']['resultMetadata']['resultCode'] not in 'SUCCESS':
                self.log.warning('problem running batch add, result code = %s',
                                 rsp_j['WsAddMemberResults']['resultMetadata']['resultCode'])
            else:
                self.log.info(f"added batch {n_batches}, " +
                              f"{len(batch)} entries, " +
                              f"{batch_t} seconds")

            if self.batch_delay > 0:
                self.log.info(f"pausing for {self.batch_delay} seconds")
                time.sleep(self.batch_delay)

        self.log.debug('finished synchronize')
        return
