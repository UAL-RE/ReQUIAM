from requiam.quota import ual_ldap_quota_query

org_codes = ['0414', '0310']


def test_ual_ldap_quota_query():

    # Consider each main classification
    for ual_class in ['faculty', 'grad', 'ugrad']:
        ldap_query = ual_ldap_quota_query(ual_class)
        assert isinstance(ldap_query, list)

        # Check handling of org_codes
        ldap_queries = ual_ldap_quota_query(ual_class, org_codes=org_codes)
        assert isinstance(ldap_queries, list)
        assert len(ldap_queries) == len(org_codes)

    # This should not return any - not in list
    ual_ldap_quota_query('test')
