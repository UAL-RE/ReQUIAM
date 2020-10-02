from .ldap_query import ual_grouper_base


def ual_ldap_quota_query(ual_class, org_codes=None):
    """
    Purpose:
      Construct RFC 4512-compatible LDAP query to search for those within
      a UAL-based classification patron group

      This function provides LDAP information for IAM accounts associated
      with default quota tiers (faculty, grad, undergrad)

      It is intended to be used with the LDAPConnection() object through
      ldap_connection.ldap_search:
        quota_query = ual_ldap_quota_query('faculty')
        members     = ldap_connection.ldap_search(ldc, quota_query)

    :param ual_class: A string to indicate types. Options are:
      'faculty' (for faculty, staff, and dcc)
      'grad'    (for graduate students)
      'ugrad'   (for undergraduate students)

    :param org_codes: List of org codes to require in search. Default: None

    :return ldap_query: list containing a single query string
    """

    if ual_class not in ['faculty', 'grad', 'ugrad']:
        print("[ual_class] must either be 'faculty', 'grad', or 'ugrad'")
        print("Exiting!")
        return

    if ual_class == 'faculty':
        ldap_query = '( | ({}) '.format(ual_grouper_base('ual-faculty')) + \
                     '({}) '.format(ual_grouper_base('ual-staff')) + \
                     '({}) )'.format(ual_grouper_base('ual-dcc'))

    if ual_class == 'grad':
        ldap_query = '({})'.format(ual_grouper_base('ual-grads'))

    if ual_class == 'ugrad':
        ldap_query = '({})'.format(ual_grouper_base('ual-ugrads'))

    # Filter by org codes
    if not isinstance(org_codes, type(None)):
        ldap_queries = [f'(& (employeePrimaryDept={oc}) {ldap_query} )' for oc in org_codes]

        return ldap_queries
    else:
        return [ldap_query]
