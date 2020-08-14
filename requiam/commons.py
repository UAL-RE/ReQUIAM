def figshare_stem(stem, production=True):
    """
    Purpose:
      Construct Grouper figshare stems

    :param stem: string corresponding to the sub-stem
       Options are: 'quota', 'portal'
    :param production: Bool to use production stem. Otherwise a stage/test is used. Default: True
    :return stem_query: str

    Usage:
      For quota stem, call as: figshare_stem('quota')
        > 'arizona.edu:dept:LBRY:figshare:quota'

      For portal stem, call as: figshare_stem('portal')
        > 'arizona.edu:dept:LBRY:figshare:portal'
    """

    if production:
        stem_query = f'arizona.edu:dept:LBRY:figshare:{stem}'
    else:
        stem_query = f'arizona.edu:dept:LBRY:devtest:chun{stem}'

    return stem_query
