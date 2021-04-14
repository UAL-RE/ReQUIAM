from typing import Optional
from .ldap_query import ual_grouper_base


def ual_ldap_quota_query(ual_class: str,
                         org_codes: Optional[list] = None) -> list:
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

    :return: List containing query/queries
    """

    if ual_class not in ['faculty', 'grad', 'ugrad']:
        print("[ual_class] must either be 'faculty', 'grad', or 'ugrad'")
        print("Exiting!")
        return

    ual_faculty = ual_grouper_base('ual-faculty')
    ual_staff = ual_grouper_base('ual-staff')
    ual_dcc = ual_grouper_base('ual-dcc')
    ual_grads = ual_grouper_base('ual-grads')
    ual_ugrads = ual_grouper_base('ual-ugrads')

    if ual_class == 'faculty':
        ldap_query = f'( | ({ual_faculty}) ' + \
                     f'({ual_staff}) ' + \
                     f'({ual_dcc}) )'

    if ual_class == 'grad':
        ldap_query = f'( & ({ual_grads}) ' + \
                     f'(! ({ual_faculty}) ) ' + \
                     f'(! ({ual_staff}) ) ' + \
                     f'(! ({ual_dcc}) ) )'

    if ual_class == 'ugrad':
        ldap_query = f'( & ({ual_ugrads}) ' + \
                     f'(! ({ual_faculty}) ) ' + \
                     f'(! ({ual_staff}) ) ' + \
                     f'(! ({ual_dcc}) )' + \
                     f'(! ({ual_grads}) ) )'

    # Filter by org codes
    if org_codes:
        return [f'(& (employeePrimaryDept={oc}) {ldap_query} )'
                for oc in org_codes]
    else:
        return [ldap_query]
