import pandas as pd

from requiam import manual_override


def test_ManualOverride():

    # Unavailable files
    std_files = {'portal_file': 'config/portal_manual.csv',
                 'quota_file': 'config/quota_manual.csv'}

    # templates
    template_files = {'portal_file': manual_override.portal_template_file,
                      'quota_file': manual_override.quota_template_file}
    mo = manual_override.ManualOverride(**template_files)
    try:
        mo.update_dataframe(['netid_test1'], ['T123456789'], 'sci_math', '')
    except ValueError:
        pass

    mo.update_dataframe(['netid_test1'], ['T123456789'], 'sci_math', 'portal')
    mo.update_dataframe(['netid_test2'], ['T987654321'], 'humanities', 'portal')
    mo.update_dataframe(['netid_test1'], ['T123456789'], 2254857830, 'quota')

    # Check removal (after add)
    mo.update_dataframe(['netid_test2'], ['T987654321'], 2254857830, 'quota')
    mo.update_dataframe(['netid_test2'], ['T987654321'], 'root', 'quota')

    # Check that nothing happens if not in list and root
    mo.update_dataframe(['netid_test3'], ['T999999999'], 'root', 'portal')

    '''
    portal_df = pd.read_csv(template_files['portal_file'], comment='#',
                            dtype=str)
    portal_df.loc[len(portal_df)] = ['netid_test1', 'T123456789', 'sci_math']
    portal_df.loc[len(portal_df)] = ['netid_test2', 'T987654321', 'humanities']
    portal_df.to_csv(template_files['portal_file'], index=False)
    '''
    for file_dict in [std_files, template_files]:
        mo = manual_override.ManualOverride(**file_dict)
        assert isinstance(mo, manual_override.ManualOverride)
        assert isinstance(mo.portal_file, str)
        assert isinstance(mo.portal_file, str)
        assert isinstance(mo.portal_df, pd.DataFrame)
        assert isinstance(mo.quota_df, pd.DataFrame)
        assert isinstance(mo.portal_header, list)
        assert isinstance(mo.quota_header, list)

    # Test identify_changes

    # Check that elements are increased
    ldap_set = {'T999999999'}
    new_ldap_set = mo.identify_changes(ldap_set, 'sci_math', 'portal')
    assert len(new_ldap_set) == len(ldap_set) + 1
    new_ldap_set = mo.identify_changes(ldap_set, 'humanities', 'portal')
    assert len(new_ldap_set) == len(ldap_set) + 1

    # Check that elements is zero
    ldap_set = {'T123456789', 'T987654321'}
    new_ldap_set = mo.identify_changes(ldap_set, 'astro', 'portal')
    assert len(new_ldap_set) == len(ldap_set) - 2

