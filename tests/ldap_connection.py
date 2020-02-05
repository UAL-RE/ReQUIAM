import ldap3
import logging

logger = logging.getLogger( __name__ )

class LDAPConnection( object ):
    '''
    Purpose:
      This class initializes a connection to a specified LDAP server.
      It allows for repeated LDAP queries. Originally patron group
      developed the connection to use with individual queries.  The
      queries have been broken off since our use with the data
      repository could involve up to 1000 queries given the number of
      different organizations that we have.


    Usage:
      Quick how to:
        from DataRepository_patrons.tests import ldap_connection, query
        eds_hostname = 'eds.arizona.edu'
        ldap_base_dn = 'dc=eds,dc=arizona,dc=edu'
        ldc = ldap_connection.LDAPConnection(eds_hostname, ldap_base_dn,
                                             USERNAME, PASSWORD)

        portal_query = ldap_connection.ual_ldap_queries(['0404', '0413', '0411'])
        members = ldap_connection.ldap_search(ldc, portal_query)
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
    """
    Purpose:
      Returns a string to use in LDAP queries that provide the Grouper
      ismemberof stem organization that UA Libraries use for patron
      management

      Note that this only returns a string, it is not RFC 4512
      compatible. See ual_ldap_query()

    :param basename: string containing Grouper group name basename.
        Options are:
            ual-dcc, ual-faculty, ual-hsl, ual-staff, ual-students,
            ual-grads, ual-ugrads

    :return: str with ismemberof attribute
    """

    return 'ismemberof=arizona.edu:dept:LBRY:pgrps:{}'.format(basename)


def ual_ldap_query(org_code):
    '''
    Construct RFC 4512-compatible LDAP query to search for those with UA
    Library privileges within an organization specified by the org_code
    input

    :param org_code: A string of the org code (e.g., '0212')

    :return ldap_query: list containing the str
    '''

    ldap_query = '(& (employeePrimaryDept={}) (| '.format(org_code)+\
                 '({}) '.format(ual_grouper_base('ual-faculty'))+\
                 '({}) '.format(ual_grouper_base('ual-staff'))+\
                 '({}) '.format(ual_grouper_base('ual-students'))+\
                 '({}) ) )'.format(ual_grouper_base('ual-dcc'))

    return [ldap_query]


def ual_ldap_queries(org_codes):
    '''
    Construct *multiple* RFC 4512-compatible LDAP queries to search for
    those with UA Library privileges within multiple organizations
    specified by the org_codes input

    :param org_codes: A list of strings containining org codes
                      (e.g., ['0212','0213','0214'])

    :return ldap_queries: list of str
    '''

    ldap_queries = [ual_ldap_query(org_code)[0] for org_code in org_codes]

    return ldap_queries


def ldap_search(ldapconnection, ldap_query):
    '''
    Function that queries a define LDAP connection and retrieve members

    :param ldapconnection: An ldap3 Connection from LDAPConnection(),
        ldapconnection = LDAPConnection(**)

    :param ldap_query: str or list of strings
        String (list of strings) containing the query (ies)

    :return member: set containing list of members
    '''

    ldap_search_dn = ldapconnection.ldap_search_dn
    ldap_attribs = ldapconnection.ldap_attribs

    # Use of set for unique entries
    all_members = set()

    for query in ldap_query:
        ldapconnection.ldc.search(ldap_search_dn, query, attributes=ldap_attribs)

        members = {e.uaid.value for e in ldapconnection.ldc.entries}
        all_members = set.union(all_members, members)

    return all_members
