from requiam import ldap_query

org_codes = ['0414', '0310']


def test_uid_query():

    query = ldap_query.uid_query('T123456789')

    assert isinstance(query, list)
    assert len(query) == 1


def test_ual_grouper_base():

    base_names = ['ual-dcc', 'ual-faculty', 'ual-hsl', 'ual-staff',
                 'ual-students', 'ual-grads', 'ual-ugrads']

    for basename in base_names:
        result = ldap_query.ual_grouper_base(basename)
        assert 'ismemberof=arizona.edu:dept:LBRY:pgrps:' in result
        assert isinstance(result, str)
        assert basename in result


def test_ual_ldap_query():

    # Consider each main classification
    for ual_class in ['none', 'all', 'faculty', 'staff', 'students', 'dcc', 'test']:
        try:
            query = ldap_query.ual_ldap_query(org_codes[0], ual_class)
            assert isinstance(query, list)
        except ValueError:
            pass


def test_ual_ldap_queries():

    queries = ldap_query.ual_ldap_queries(org_codes)

    assert isinstance(queries, list)
    assert len(queries) == len(org_codes)
