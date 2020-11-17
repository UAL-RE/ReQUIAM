from requiam.grouper_query import figshare_group

prod_stem = 'arizona.edu:dept:LBRY:figshare'
stage_stem = 'arizona.edu:dept:LBRY:figtest'


def test_figshare_group():

    for group in ['astro', 'sci_math', 'test']:
        f_group = figshare_group(group, 'portal', production=False)
        assert f_group == f"{stage_stem}:portal:{group}"

        f_group = figshare_group(group, 'portal', production=True)
        assert f_group == f"{prod_stem}:portal:{group}"

    for quota in [104857600, 536870912, 2147483648]:
        f_group = figshare_group(quota, 'quota', production=False)
        assert f_group == f"{stage_stem}:quota:{quota}"
        f_group = figshare_group(quota, 'quota', production=True)
        assert f_group == f"{prod_stem}:quota:{quota}"
