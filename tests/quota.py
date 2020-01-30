from .ldap_connection import ual_grouper_base

def ual_ldap_quota_query(ual_class):
    '''
    Construct RFC 4512-compatible LDAP query to search for those within
    a UAL-based classification patron group to set default quota

    :param ual_class: A string to indicate types. Options are:
    'faculty'   (for faculty and staff)
    'grad'      (for grad students)
    'undergrad' (for undergraduate)

    :return ldap_query: list containing a single query string
    '''

    if ual_class == 'faculty':
        ldap_query = '( | ({}) '.format(ual_grouper_base('ual-faculty'))+\
                     '({}) '.format(ual_grouper_base('ual-staff'))+\
                     '({}) )'.format(ual_grouper_base('ual-dcc'))

    if ual_class == 'grad':
        ldap_query = '({})'.format(ual_grouper_base('ual-grads'))

    if ual_class == 'undergrad':
        ldap_query = '({})'.format(ual_grouper_base('ual-undergrads'))

    return [ldap_query]
