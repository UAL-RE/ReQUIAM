from logging import Logger
import ldap3

from redata.commons.logger import log_stdout


class LDAPConnection:
    """
    This class initializes a connection to a specified LDAP/EDS server.
    It allows for repeated LDAP queries. Originally patron group
    developed the connection to use with individual queries.  The
    queries have been broken off since our use with the data
    repository could involve up to 1000 queries given the number of
    different organizations that we have.

    Usage:

    .. highlight:: python
    .. code-block:: python

        from requiam import ldap_query
        eds_hostname = 'eds.arizona.edu'
        ldap_base_dn = 'dc=eds,dc=arizona,dc=edu'
        ldc = ldap_query.LDAPConnection(eds_hostname, ldap_base_dn,
                                        USERNAME, PASSWORD)

        portal_query = ldap_query.ual_ldap_queries(['0404', '0413', '0411'])
        members = ldap_query.ldap_search(ldc, portal_query)

    :param ldap_host: LDAP host URL
    :param ldap_base_dn: LDAP base distinguished name
    :param ldap_user: LDAP username
    :param ldap_password: LDAP password credentials
    :param log: File and/or stdout logging. Default: ``log_stdout``

    :ivar ldap_host: LDAP host URL
    :ivar ldap_base_dn: LDAP base distinguished name
    :ivar ldap_user: LDAP username
    :ivar ldap_password: LDAP password credentials
    :ivar log: File and/or stdout logging
    :ivar str ldap_bind_host: LDAP binding host URL
    :ivar str ldap_bind_dn: LDAP binding distinguished name
    :ivar str ldap_search_dn: LDAP search distinguished name
    :ivar list ldap_attribs: LDAP attributes. Set to "uaid"
    """

    def __init__(self, ldap_host: str, ldap_base_dn: str,
                 ldap_user: str, ldap_password: str,
                 log: Logger = log_stdout()) -> None:

        log.debug('entered')
        
        #
        # set properties

        self.ldap_host = ldap_host
        self.ldap_base_dn = ldap_base_dn
        self.ldap_user = ldap_user
        self.ldap_password = ldap_password

        self.ldap_bind_host: str = f"ldaps://{ldap_host}"
        self.ldap_bind_dn: str = f"uid={ldap_user},ou=app users,{ldap_base_dn}"
        self.ldap_search_dn: str = f"ou=people,{ldap_base_dn}"
        self.ldap_attribs: list = ['uaid']

        #
        # execute ldap query and populate members property

        self.ldc = ldap3.Connection(self.ldap_bind_host, self.ldap_bind_dn,
                                    self.ldap_password, auto_bind=True)

        log.debug('returning')


def uid_query(uid: str) -> list:
    """
    Construct RFC 4512-compatible LDAP query for a single NetID account

    Usage:

    .. highlight:: python
    .. code-block:: python

        ldap_query = ldap_query.ual_test_query('<netid>')
        > ['(uid=<netid>)']

    :param uid: NetID handle/username
    :return: LDAP query
    """

    ldap_query = f"(uid={uid})"

    return [ldap_query]


def ual_grouper_base(basename: str) -> str:
    """
    Returns a string to use in LDAP queries that provide the Grouper
    ismemberof stem organization that UA Libraries use for patron
    management

    Note that this only returns a string, it is not RFC 4512
    compatible. See :func:`requiam.ldap_query.ual_ldap_query`

    Usage:

    .. highlight:: python
    .. code-block:: python

        grouper_base = ldap_query.ual_grouper_base('ual-faculty')
        > "ismemberof=arizona.edu:dept:LBRY:pgrps:ual-faculty"

    :param basename: Grouper group name basename.
           Options are: ual-dcc, ual-faculty, ual-hsl, ual-staff,
           ual-students, ual-grads, ual-ugrads

    :return: ``ismemberof`` attribute
    """

    return f"ismemberof=arizona.edu:dept:LBRY:pgrps:{basename}"


def ual_ldap_query(org_code: str, classification: str = 'all') -> list:
    """
    Construct RFC 4512-compatible LDAP query to search for those with UArizona
    Library privileges within an organization (specified by ``org_code``)

    Usage:

    .. highlight:: python
    .. code-block:: python

        ldap_query = ldap_query.ual_ldap_query('0212')
        > ['(& (employeePrimaryDept=0212) (|
            (ismemberof=arizona.edu:dept:LBRY:pgrps:ual-faculty)
            (ismemberof=arizona.edu:dept:LBRY:pgrps:ual-staff)
            (ismemberof=arizona.edu:dept:LBRY:pgrps:ual-students)
            (ismemberof=arizona.edu:dept:LBRY:pgrps:ual-dcc) ) )']

    :param org_code: Organizational code (e.g., '0212')
    :param classification: Input for classification. Default: 'all'.
           Others: 'faculty', 'staff', 'students', 'dcc', 'none'
           The 'none' input will provide ``org_code``-only query

    :return: List of LDAP queries
    """

    if classification == 'none':
        ldap_query = f"(employeePrimaryDept={org_code})"
    else:
        ldap_query = f"(& (employeePrimaryDept={org_code}) (| "

        classification_list = ['all', 'faculty', 'staff', 'students', 'dcc']
        if classification not in classification_list:
            raise ValueError("Incorrect members input")

        if classification == 'all':
            for member in classification_list[1:]:
                group_str = ual_grouper_base(f"ual-{member}")
                ldap_query += f"({group_str}) "
        else:
            group_str = ual_grouper_base(f"ual-{classification}")
            ldap_query += f"({group_str}) "

        ldap_query += ") )"

    return [ldap_query]


def ual_ldap_queries(org_codes: list) -> list:
    """
    Purpose:
      Construct *multiple* RFC 4512-compatible LDAP queries to search for
      those with UA Library privileges within multiple organizations
      specified by the org_codes input


    Usage:

    .. highlight:: python
    .. code-block:: python

       ldap_queries = ldap_query.ual_ldap_queries(['0212','0213','0214'])


    :param org_codes: A list of strings containining org codes
                      (e.g., ['0212','0213','0214'])

    :return ldap_queries: list of str
    """

    ldap_queries = [ual_ldap_query(org_code)[0] for org_code in org_codes]

    return ldap_queries


def ldap_search(ldapconnection: LDAPConnection, ldap_query: list) -> set:
    """
    Queries a define LDAP connection and retrieve members

    Usage (see description in :class:`requiam.ldap_query.LDAPConnection`):

    .. highlight:: python
    .. code-block:: python

       members = ldap_query.ldap_search(ldc, ldap_query)

    :param ldapconnection: An ``ldap3`` ``Connection`` from
           :class:`requiam.ldap_query.LDAPConnection`
    :param ldap_query: List of strings from :func:`requiam.ldap_query.ual_ldap_queries`

    :return: List of members
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
