def figshare_stem(stem):
    """
    Purpose:
      Construct Grouper figshare stems

    :param stem: string corresponding to the sub-stem
       Options are: 'quota', 'portal'

    :return stem_query: str

    Usage:
      For quota stem, call as: figshare_stem('quota')
        > 'arizona.edu:dept:LBRY:figshare:quota'

      For portal stem, call as: figshare_stem('portal')
        > 'arizona.edu:dept:LBRY:figshare:portal'
    """

    stem_query = 'arizona.edu:dept:LBRY:figshare:{}'.format(stem)
    return stem_query
