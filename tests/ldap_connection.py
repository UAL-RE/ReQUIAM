import ldap3
import logging

logger = logging.getLogger( __name__ )

class LDAPConnection( object ):
    '''

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
