import ldap3
import logging

logger = logging.getLogger( __name__ )

class LDAPConnection( object ):
    
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
