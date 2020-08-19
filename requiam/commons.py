def figshare_stem(stem='', production=True):
    """
    Purpose:
      Construct Grouper figshare stems

    :param stem: string corresponding to the sub-stem
       Some options are: 'quota', 'portal'. Default: root stem
    :param production: Bool to use production stem. Otherwise a stage/test is used. Default: True
    :return stem_query: str

    Usage:
      For quota stem, call as: figshare_stem('quota')
        > 'arizona.edu:dept:LBRY:figshare:quota'

      For portal stem, call as: figshare_stem('portal')
        > 'arizona.edu:dept:LBRY:figshare:portal'

      For main stem, call as: figshare_stem()
        > 'arizona.edu:dept:LBRY:figshare'
    """

    if production:
        stem_query = 'arizona.edu:dept:LBRY:figshare'
    else:
        stem_query = 'arizona.edu:dept:LBRY:figtest'

    # If [stem] is not an empty string
    if stem:
        stem_query += f':{stem}'

    return stem_query
