import datetime
import json
import logging
import requests
import time

logger = logging.getLogger(__name__)


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
        from DataRepository_patrons.tests import delta

    """

    def __init__(self, ldap_members, grouper_query_instance, batch_size,
                 batch_timeout, batch_delay, sync_max):
        logger.debug('entered')

        self.ldap_members = ldap_members
        self.grouper_query_instance = grouper_query_instance
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.batch_delay = batch_delay
        self.sync_max = sync_max

        logger.debug('returning')
        return

    @property
    def common(self):
        logger.debug('entered')

        common = self.ldap_members & self.grouper_query_instance.members

        logger.debug('returning')
        return common

    @property
    def adds(self):
        logger.debug('entered')

        adds = self.ldap_members - self.grouper_query_instance.members

        logger.debug('returning')
        return adds

    @property
    def drops(self):
        logger.debug('entered')

        drops = self.grouper_query_instance.members - self.ldap_members

        logger.debug('returning')
        return drops

    def synchronize(self):
        logger.debug('entered')

        total_delta = len(list(self.adds)) + len(list(self.drops))
        if total_delta > self.sync_max:
            logger.warning(
                'total delta (%d) exceeds maximum sync limit (%d), will not synchronize' % (total_delta, self.sync_max))
            logger.debug('returning')
            return

        logger.info('synchronizing ldap query results to %s' % self.grouper_query_instance.grouper_group)
        logger.info('batch size = %d, batch timeout = %d seconds, batch delay = %d seconds' %
                    (self.batch_size, self.batch_timeout, self.batch_delay))

        logger.info('processing drops:')
        n_batches = 0
        list_of_drops = list(self.drops)
        for batch in [list_of_drops[i:i + self.batch_size] for i in range(0, len(list_of_drops), self.batch_size)]:
            n_batches += 1

            start_t = datetime.datetime.now()
            rsp = requests.post(self.grouper_query_instance.grouper_group_members_url,
                                auth=(self.grouper_query_instance.grouper_user,
                                      self.grouper_query_instance.grouper_password),
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
                logger.warning('problem running batch delete, result code = %s',
                               rsp_j['WsDeleteMemberResults']['resultMetadata']['resultCode'])
            else:
                logger.info('dropped batch %d, %d entries, %d seconds' % (n_batches, len(batch), batch_t))

            if self.batch_delay > 0:
                logger.info('pausing for %d seconds' % self.batch_delay)
                time.sleep(self.batch_delay)

        logger.info('processing adds:')
        n_batches = 0
        list_of_adds = list(self.adds)
        for batch in [list_of_adds[i:i + self.batch_size] for i in range(0, len(list_of_adds), self.batch_size)]:
            n_batches += 1

            start_t = datetime.datetime.now()
            rsp = requests.put(self.grouper_query_instance.grouper_group_members_url,
                               auth=(self.grouper_query_instance.grouper_user,
                                     self.grouper_query_instance.grouper_password),
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
                logger.warning('problem running batch add, result code = %s',
                               rsp_j['WsAddMemberResults']['resultMetadata']['resultCode'])
            else:
                logger.info('added batch %d, %d entries, %d seconds' % (n_batches, len(batch), batch_t))

            if self.batch_delay > 0:
                logger.info('pausing for %d seconds' % self.batch_delay)
                time.sleep(self.batch_delay)

        logger.debug('returning')
        return
