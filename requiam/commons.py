import configparser


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


def dict_load(config_file, vargs=None):
    """
    Purpose:
      Read in a config INI file using configparser and return a dictionary
      with sections and options

    :param config_file: str. Full/relative path of configuration file
    :param vargs: dict containing command-line arguments
    :return config_dict: dict of dict with hierarchy for config sections
    """

    if vargs is None:
        vargs = dict()

    config = configparser.ConfigParser()
    config.read(config_file)

    # Read in default settings
    config_dict = {}
    for section in config.sections():
        config_dict[section] = {}
        for option in config.options(section):
            option_input = config.get(section, option)
            if option_input in ['True', 'False']:
                config_dict[section][option] = config.getboolean(section, option)
            else:
                if option_input.isdigit():  # set as integer
                    config_dict[section][option] = int(option_input)
                else:
                    config_dict[section][option] = config.get(section, option)

    # Populate with command-line arguments overrides
    config_dict['extras'] = {}
    if vargs:
        for p in vargs.keys():
            if vargs[p] is not None:
                if p in config_dict['global']:
                    # If input argument is set, override global settings
                    config_dict['global'][p] = vargs[p]
                else:
                    if p in config_dict['google']:
                        config_dict['google'][p] = vargs[p]
                    else:
                        # Add to extras dictionary
                        config_dict['extras'][p] = vargs[p]
            else:
                if (p not in config_dict['global']) and \
                        (p not in config_dict['google']):
                    config_dict['extras'][p] = '(unset)'

    return config_dict


def get_summary_dict(ldap_members, grouper_members, delta):
    """
    Purpose:
      Return a dict containing summary data for EDS and Grouper queries

    :param ldap_members: set containing EDS entries
    :param grouper_members: set containing Grouper entries
    :param delta: Delta object containing computation of adds and drops
    :return: summary_dict: dict containing summary data
    """

    summary_dict = {
        'num_EDS': len(ldap_members),
        'num_Grouper': len(grouper_members),
        'adds': len(delta.adds),
        'drops': len(delta.drops),
        'total': len(delta.adds) + len(delta.drops)
    }
    return summary_dict
