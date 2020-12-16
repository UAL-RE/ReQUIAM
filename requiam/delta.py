import datetime
import json
import requests
import time

from .logger import log_stdout


class Delta(object):
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

    def __init__(self, ldap_members, grouper_query_instance, batch_size,
                 batch_timeout, batch_delay, sync_max, log=None):

        if isinstance(log, type(None)):
            self.log = log_stdout()
        else:
            self.log = log

        self.log.debug('entered')

        self.ldap_members = ldap_members
        self.grouper_qry = grouper_query_instance
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.batch_delay = batch_delay
        self.sync_max = sync_max

        self.drops = self._drops()
        self.adds = self._adds()
        self.common = self._common()

        self.log.debug('returning')
        return

    def _common(self):
        common = self.ldap_members & self.grouper_qry.members

        self.log.debug('finished common')
        return common

    def _adds(self):
        adds = self.ldap_members - self.grouper_qry.members

        self.log.debug('finished adds')
        return adds

    def _drops(self):
        drops = self.grouper_qry.members - self.ldap_members

        self.log.debug('finished drops')
        return drops

    def synchronize(self):
        self.log.debug('entered')

        total_delta = len(list(self.adds)) + len(list(self.drops))
        if total_delta > self.sync_max:
            self.log.warning(f"total delta ({total_delta}) exceeds maximum " +
                             f"sync limit ({self.sync_max}), will not synchronize")
            self.log.debug('finished synchronize')
            return

        self.log.info(f"synchronizing ldap query results to {self.grouper_qry.grouper_group}")
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
            rsp = requests.post(self.grouper_qry.grouper_group_members_url,
                                auth=(self.grouper_qry.grouper_user,
                                      self.grouper_qry.grouper_password),
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
            rsp = requests.put(self.grouper_qry.grouper_group_members_url,
                               auth=(self.grouper_qry.grouper_user,
                                     self.grouper_qry.grouper_password),
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
                              "{batch_t} seconds")

            if self.batch_delay > 0:
                self.log.info(f"pausing for {self.batch_delay} seconds")
                time.sleep(self.batch_delay)

        self.log.debug('finished synchronize')
        return
