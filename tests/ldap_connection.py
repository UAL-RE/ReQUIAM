import ldap3
import logging

logger = logging.getLogger( __name__ )

class LDAPConnection( object ):
    '''
    This class initializes a connection to a specified LDAP server.  It
    allows for repeated LDAP queries. Originally patron group developed
    the connection to use with individual queries.  The queries have
    been broken off since our use with the data repository could
    involve up to 1000 queries given the number of different
    organizations that we have.

    Quick how to:

    from DataRepository_patrons.tests import ldap_connection
    eds_hostname = 'eds.arizona.edu'
    ldap_base_dn = 'dc=eds,dc=arizona,dc=edu'
    ldc = ldap_connection.LDAPConnection(eds_hostname, ldap_base_dn, USERNAME, PASSWORD)

    ldap_search_dn = 'ou=people,' + ldap_base_dn
    ldap_attribs = [ 'uaid' ]

    ldap_query = '(& (employeePrimaryDept=0404) )'
    ldc.ldc.search(ldap_search_dn, ldap_query, attributes = ldap_attribs )

    # You can retrieve the uaid via:
    members = {e.uaid.value for e in ldc.ldc.entries}
    '''

    def __init__( self, ldap_host, ldap_base_dn, ldap_user, ldap_passwd):
        logger.debug( 'entered' )
        
        #
        # set properties
        
        self.ldap_host = ldap_host
        self.ldap_base_dn = ldap_base_dn
        self.ldap_user = ldap_user
        self.ldap_passwd = ldap_passwd

        self.ldap_bind_host = 'ldaps://' + ldap_host
        self.ldap_bind_dn = 'uid=' + ldap_user + ',ou=app users,' + ldap_base_dn
        self.ldap_search_dn = 'ou=people,' + ldap_base_dn
        self.ldap_attribs = [ 'uaid' ]
        
        #
        # execute ldap query and populate members property

        self.ldc = ldap3.Connection( self.ldap_bind_host, self.ldap_bind_dn, self.ldap_passwd, auto_bind = True )

        logger.debug( 'returning' )

def ual_grouper_base(basename):
    '''
    Returns a string to use in LDAP queries that provide the Grouper
    ismemberof stem organization that UA Libraries use for patron
    management

    Note that this only provides the string, it is not RFC 4512
    compatible. See ual_ldap_query()

    :param basename: string containing Grouper group name basename.
        Options are:
            ual-dcc, ual-faculty, ual-hsl, ual-staff, ual-students
    :return:
    '''

    return 'ismemberof=arizona.edu:dept:LBRY:pgrps:{}'.format(basename)


def ual_ldap_query(org_code):
    '''
    Construct RFC 4512-compatible LDAP query to search for those with UA
    Library privileges within an organization specified by the org_code
    input

    :param org_code: A string of the org code (e.g., '0212')

    :return ldap_query: str
    '''

    ldap_query = '(& (employeePrimaryDept={}) (| '.format(org_code)+\
                 '({}) '.format(ual_grouper_base('ual-faculty')+\
                 '({}) '.format(ual_grouper_base('ual-staff')+\
                 '({}) '.format(ual_grouper_base('ual-students')+\
                 '({}) ) )'.format(ual_grouper_base('ual-dcc')

    return ldap_query

def ldap_search(ldapconnection, ldap_query):
    '''
    Function that queries a define LDAP connection and retrieve members

    :param ldapconnection: An ldap3 Connection from LDAPConnection(),
        ldapconnection = LDAPConnection(**)

    :param ldap_query: str
        String containing the query

    :return member: set containing list of members
    '''

    ldap_search_dn = ldapconnection.ldap_search_dn
    ldap_attribs = ldapconnection.ldap_attribs
    ldapconnection.ldc.search(ldap_search_dn, ldap_query, attributes=ldap_attribs)

    # Use of set for unique entries
    members = {e.uaid.value for e in ldapconnection.ldc.entries}

    return members

def merge_ldap_search():
    '''
    Function that merges the results of different LDAP queries.

    Rationale:
    A "portal" (particularly a high-level research theme, e.g., Sci & Math)
    may have multiple organizations in it. Thus, a comparison between
    EDS and Grouper will not provide a proper list of additions and
    deletions.

    To conduct a proper comparison, multiple org-based queries are
    first needed. This function merges the results from those
    queries
    '''