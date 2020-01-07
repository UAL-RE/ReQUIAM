#!/Applications/anaconda3/envs/figshare/bin/python

import argparse
import configparser
#import ldap3
import logging
#import os
import petal
#import requests
import slack_log_handler


if __name__ == '__main__':

    #
    # parse command line arguments

    parser = argparse.ArgumentParser(description='Command-line driver for patron group ETL jobs.')
    parser.add_argument('--config', required=True, help='path to configuration file for this ETL run')
    parser.add_argument('--group', required=True,
                        help='name of patron group (a.k.a. section) in configuration file for this ETL run')
    parser.add_argument('--ldap_host', help='LDAP host')
    parser.add_argument('--ldap_base_dn', help='base DN for LDAP bind and query')
    parser.add_argument('--ldap_user', help='user name for LDAP login')
    parser.add_argument('--ldap_passwd', help='password for LDAP login')
    parser.add_argument('--ldap_query', help='query string for LDAP search')
    parser.add_argument('--grouper_host', help='Grouper host')
    parser.add_argument('--grouper_base_path', help='base path for Grouper API')
    parser.add_argument('--grouper_user', help='user name for Grouper login')
    parser.add_argument('--grouper_passwd', help='password for Grouper login')
    parser.add_argument('--grouper_stem', help='stem for Grouper query and update')
    parser.add_argument('--grouper_group', help='group for Grouper query and update')
    parser.add_argument('--batch_size', help='synchronization batch size')
    parser.add_argument('--batch_timeout', help='synchronization batch timeout in seconds')
    parser.add_argument('--batch_delay', help='delay between batches in seconds')
    parser.add_argument('--sync', action='store_true', help='perform synchronization')
    parser.add_argument('--sync_max', help='maximum membership delta to allow when synchronizing')
    parser.add_argument('--debug', action='store_true', help='turn on debug logging')
    parser.add_argument('--slack', help='redirect logging to Slack webhook')
    args = parser.parse_args()

    #
    # setup logging

    logger = logging.getLogger(__name__)
    if args.slack:
        handler = slack_log_handler.SlackLogHandler(args.slack, username='petl')
        format = '%(levelname)s '
    else:
        handler = logging.StreamHandler()
        format = '%(asctime)s %(levelname)s '
    if args.debug:
        format += '%(name)s %(funcName)s(): %(message)s'
    else:
        format += '%(message)s'
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    petal.logger.addHandler(handler)
    if args.debug:
        logger.setLevel(logging.DEBUG)
        petal.logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        petal.logger.setLevel(logging.INFO)

    #
    # tag top of run

    if args.slack:
        logger.info('----------[ petl script executing ]----------')
    logger.info('starting run:')
    logger.info('    config = %s', args.config)
    logger.info('    group = %s', args.group)

    #
    # load parameters from specified configuration file, fold into command-line overrides

    config = configparser.ConfigParser()
    config.read(args.config)

    vargs = vars(args)
    for p in ['ldap_host', 'ldap_base_dn', 'ldap_user', 'ldap_passwd', 'ldap_query',
              'grouper_host', 'grouper_base_path', 'grouper_user', 'grouper_passwd', 'grouper_stem', 'grouper_group',
              'batch_size', 'batch_timeout', 'batch_delay', 'sync_max']:

        if (p in vargs) and (vargs[p] is not None):
            vargs[p] = vargs[p]
        elif (p in config[args.group]) and (config[args.group][p] is not None):
            vargs[p] = config[args.group][p]
        elif (p in config['global']) and (config['global'][p] is not None):
            vargs[p] = config['global'][p]
        else:
            vargs[p] = '(unset)'

        if p in ['ldap_passwd', 'grouper_passwd']:
            if vargs[p] is '(unset)':
                logger.debug('    %s = (unset)', p)
            else:
                logger.debug('    %s = (set)', p)
        else:
            logger.debug('    %s = %s', p, vargs[p])

    logger.debug('    sync = %s', args.sync)
    logger.debug('    debug = %s', args.debug)

    #
    # instantiate ldap query object

    lq = petal.LDAPQuery(ldap_host=vargs['ldap_host'],
                         ldap_base_dn=vargs['ldap_base_dn'],
                         ldap_user=vargs['ldap_user'],
                         ldap_passwd=vargs['ldap_passwd'],
                         ldap_query=vargs['ldap_query'])
    logger.info('found %d entries via LDAP query', len(lq.members))

    #
    # exit successfully

    logger.info('run complete.')
    if args.slack:
        logger.info('----------[ petl script exiting ]----------')

    exit(0)
