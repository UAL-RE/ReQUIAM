import ldap3
import logging

logger = logging.getLogger(__name__)


class LDAPConnection(object):
    """
    Purpose:
      This class initializes a connection to a specified LDAP server.
      It allows for repeated LDAP queries. Originally patron group
      developed the connection to use with individual queries.  The
      queries have been broken off since our use with the data
      repository could involve up to 1000 queries given the number of
      different organizations that we have.


    Usage:
      Quick how to:
        from ReQUIAM import ldap_query
        eds_hostname = 'eds.arizona.edu'
        ldap_base_dn = 'dc=eds,dc=arizona,dc=edu'
        ldc = ldap_query.LDAPConnection(eds_hostname, ldap_base_dn,
                                        USERNAME, PASSWORD)

        portal_query = ldap_query.ual_ldap_queries(['0404', '0413', '0411'])
        members = ldap_query.ldap_search(ldc, portal_query)
    """

    def __init__(self, ldap_host, ldap_base_dn, ldap_user, ldap_password):
        logger.debug('entered')
        
        #
        # set properties
        
        self.ldap_host = ldap_host
        self.ldap_base_dn = ldap_base_dn
        self.ldap_user = ldap_user
        self.ldap_password = ldap_password

        self.ldap_bind_host = 'ldaps://' + ldap_host
        self.ldap_bind_dn = 'uid=' + ldap_user + ',ou=app users,' + ldap_base_dn
        self.ldap_search_dn = 'ou=people,' + ldap_base_dn
        self.ldap_attribs = ['uaid']
        
        #
        # execute ldap query and populate members property

        self.ldc = ldap3.Connection(self.ldap_bind_host, self.ldap_bind_dn,
                                    self.ldap_password, auto_bind=True)

        logger.debug('returning')


def uid_query(uid):
    """
    Purpose:
      Construct RFC 4512-compatible LDAP query for a single NetID account

    Usage:
      ldap_query = ldap_query.ual_test_query('<netid>)
        > ['(uid=<netid>)']

    :param uid: str of NetID handle
    :return ldap_query: list containing the str
    """

    ldap_query = '(uid={})'.format(uid)

    return [ldap_query]


def ual_grouper_base(basename):
    """
    Purpose:
      Returns a string to use in LDAP queries that provide the Grouper
      ismemberof stem organization that UA Libraries use for patron
      management

      Note that this only returns a string, it is not RFC 4512
      compatible. See ual_ldap_query()


    Usage:
      grouper_base = ldap_query.ual_grouper_base('ual-faculty')
        > ismemberof=arizona.edu:dept:LBRY:pgrps:ual-faculty

    :param basename: string containing Grouper group name basename.
        Options are:
            ual-dcc, ual-faculty, ual-hsl, ual-staff, ual-students,
            ual-grads, ual-ugrads

    :return: str with ismemberof attribute
    """

    return 'ismemberof=arizona.edu:dept:LBRY:pgrps:{}'.format(basename)


def ual_ldap_query(org_code, members='all'):
    """
    Purpose:
      Construct RFC 4512-compatible LDAP query to search for those with UA
      Library privileges within an organization specified by the org_code
      input


    Usage:
      ldap_query = ldap_query.ual_ldap_query('0212')
        > ['(& (employeePrimaryDept=0212) (|
            (ismemberof=arizona.edu:dept:LBRY:pgrps:ual-faculty)
            (ismemberof=arizona.edu:dept:LBRY:pgrps:ual-staff)
            (ismemberof=arizona.edu:dept:LBRY:pgrps:ual-students)
            (ismemberof=arizona.edu:dept:LBRY:pgrps:ual-dcc) ) )']


    :param org_code: A string of the org code (e.g., '0212')
    :param members: Optional string input. Default: 'all'.
                    Others: 'faculty', 'staff', 'student', 'dcc'
    :return ldap_query: list containing the str
    """

    ldap_query = '(& (employeePrimaryDept={}) (| '.format(org_code)

    classification_list = ['all', 'faculty', 'staff', 'student', 'dcc']
    if members not in classification_list:
        raise ValueError("Incorrect members input")

    if members == 'all':
        for member in classification_list[1:]:
            ldap_query += '({}) '.format(ual_grouper_base(f'ual-{member}'))
    else:
        ldap_query += '({}) '.format(ual_grouper_base(f'ual-{members}'))

    ldap_query += ') )'

    return [ldap_query]


def ual_ldap_queries(org_codes):
    """
    Purpose:
      Construct *multiple* RFC 4512-compatible LDAP queries to search for
      those with UA Library privileges within multiple organizations
      specified by the org_codes input


    Usage:
      ldap_queries = ldap_query.ual_ldap_queries(['0212','0213','0214'])


    :param org_codes: A list of strings containining org codes
                      (e.g., ['0212','0213','0214'])

    :return ldap_queries: list of str
    """

    ldap_queries = [ual_ldap_query(org_code)[0] for org_code in org_codes]

    return ldap_queries


def ldap_search(ldapconnection, ldap_query):
    """
    Purpose:
      Function that queries a define LDAP connection and retrieve members


    Usage (see description in LDAPConnection:
      members = ldap_query.ldap_search(ldc, ldap_query)

    :param ldapconnection: An ldap3 Connection from LDAPConnection(),
        ldapconnection = LDAPConnection(**)

    :param ldap_query: list of strings
        String (list of strings) containing the query(ies)

    :return member: set containing list of members
    """

    ldap_search_dn = ldapconnection.ldap_search_dn
    ldap_attribs = ldapconnection.ldap_attribs

    # Use of set for unique entries
    all_members = set()

    for query in ldap_query:
        ldapconnection.ldc.search(ldap_search_dn, query, attributes=ldap_attribs)

        members = {e.uaid.value for e in ldapconnection.ldc.entries}
        all_members = set.union(all_members, members)

    return all_members
