from typing import Dict, Optional, Union

import configparser
from requiam.delta import Delta


def figshare_stem(stem: str = '', production: bool = True) -> str:
    """
    Construct Grouper figshare stems

    :param stem: string corresponding to the sub-stem.
           Options are: 'quota', 'portal'. Default: root stem
    :param production: Bool to use production stem.
           Otherwise a stage/test is used. Default: ``True``

    :return: Grouper stem/folder string

    Usage:

    For quota stem, call as: ``figshare_stem('quota')``
       > "arizona.edu:dept:LBRY:figshare:quota"

    For portal stem, call as: ``figshare_stem('portal')``
       > "arizona.edu:dept:LBRY:figshare:portal"

    For main stem, call as: ``figshare_stem()``
       > "arizona.edu:dept:LBRY:figshare"
    """

    if production:
        stem_query = 'arizona.edu:dept:LBRY:figshare'
    else:
        stem_query = 'arizona.edu:dept:LBRY:figtest'

    # If stem is not an empty string
    if stem:
        stem_query += f':{stem}'

    return stem_query


def figshare_group(group: Union[str, int], root_stem: str,
                   production: bool = True) -> str:
    """
    Construct Grouper figshare groups

    :param group: Group name
    :param root_stem: Grouper stem/folder for ``group``
    :param production: Bool to use production stem.
           Otherwise a stage/test is used. Default: ``True``

    :return: Grouper group string

    Usage:

    For active group, call as: figshare_group('active', '')
       > "arizona.edu:dept:LBRY:figshare:active"

    For a quota group, call as: figshare_group('2147483648', 'quota')
       > "arizona.edu:dept:LBRY:figshare:quota:2147483648"

    For a portal group, call as: figshare_group('sci_math', 'portal')
       > "arizona.edu:dept:LBRY:figshare:portal:sci_math"
    """

    if not group:
        raise ValueError("WARNING: Empty [group]")

    stem_query = figshare_stem(stem=root_stem, production=production)

    grouper_group = f'{stem_query}:{group}'

    return grouper_group


def int_conversion(string: str) -> Union[int, str]:
    """
    Check and convert string that can be represented as an integer

    :param string: Input string

    :return: Result of conversion
    """
    try:
        value = int(string)
    except ValueError:
        value = string
    return value


def dict_load(config_file: str, vargs: Optional[Dict[str, str]] = None) \
        -> dict:
    """
    Read in a config INI file using ``configparser`` and return a ``dict``
    with sections and options

    :param config_file: Full/relative path of configuration file
    :param vargs: Command-line arguments from script

    :return: Python ``dict`` of configuration settings
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
    Return a dict containing summary data for EDS and Grouper queries

    :param ldap_members: set containing EDS entries
    :param grouper_members: set containing Grouper entries
    :param delta: Delta object containing computation of adds and drops

    :return: Python ``dict`` of containing summary data
    """

    summary_dict = {
        'num_EDS': len(ldap_members),
        'num_Grouper': len(grouper_members),
        'adds': len(delta.adds),
        'drops': len(delta.drops),
        'total': len(delta.adds) + len(delta.drops)
    }
    return summary_dict
