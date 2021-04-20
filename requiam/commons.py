import configparser
from requiam.delta import Delta
from typing import Dict, Optional


def figshare_stem(stem: str = '', production: bool = True) -> str:
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


def figshare_group(group: str, root_stem: str, production: bool = True) -> str:
    """
    Purpose:
      Construct Grouper figshare groups

    :param group: str or int of group name. Cannot be empty
    :param root_stem: str of associated stem folder for [group]
    :param production: Bool to use production stem. Otherwise a stage/test is used. Default: True

    :return grouper_group: str containing full Grouper path

    Usage:
      For active group, call as: figshare_group('active', '')
        > 'arizona.edu:dept:LBRY:figshare:active'

      For a quota group, call as: figshare_group('2147483648', 'quota')
        > 'arizona.edu:dept:LBRY:figshare:quota:2147483648'
      Note: group can be specified as an integer for quota cases

      For a portal group, call as: figshare_group('sci_math', 'portal')
        > 'arizona.edu:dept:LBRY:figshare:portal:sci_math'
    """

    if not group:
        raise ValueError("WARNING: Empty [group]")

    stem_query = figshare_stem(stem=root_stem, production=production)

    grouper_group = f'{stem_query}:{group}'

    return grouper_group


def int_conversion(string):
    try:
        value = int(string)
    except ValueError:
        value = string
    return value


def dict_load(config_file: str, vargs: Optional[Dict[str, str]] = None) \
        -> dict:
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
                    config_dict['global'][p] = int_conversion(vargs[p])
                else:
                    if p in config_dict['google']:
                        config_dict['google'][p] = int_conversion(vargs[p])
                    else:
                        # Add to extras dictionary
                        config_dict['extras'][p] = int_conversion(vargs[p])
            else:
                if (p not in config_dict['global']) and \
                        (p not in config_dict['google']):
                    config_dict['extras'][p] = '(unset)'

    return config_dict


def get_summary_dict(ldap_members: set, grouper_members: set, delta: Delta) \
                     -> Dict[str, int]:
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
