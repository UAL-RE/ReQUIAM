from os import path

# For database/CSV
import pandas as pd
import numpy as np
from urllib.error import URLError

# For LDAP query
from ReQUIAM.ldap_query import ual_grouper_base, ual_ldap_query, ldap_search, LDAPConnection

# Logging
from ReQUIAM import TimerClass

from datetime import date, datetime

import configparser
import argparse

today = date.today()


def get_numbers(lc, org_url):
    """
    Purpose:
      Determine number of individuals in each organization code with
      Library privileges

    :param lc: LDAPConnection() object
    :param org_url: URL that provides CSV
    :return ldc:
    """

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

    try:
        df = pd.read_csv(org_url)

        n_org_codes = df.shape[0]
        print(f"Number of organizational codes : {n_org_codes}")

        org_codes = df['Organization Code'].values

        # Arrays for members with library privileges based on classification
        total       = np.zeros(n_org_codes, dtype=int)
        lib_total   = np.zeros(n_org_codes, dtype=int)
        lib_faculty = np.zeros(n_org_codes, dtype=int)
        lib_staff   = np.zeros(n_org_codes, dtype=int)
        lib_student = np.zeros(n_org_codes, dtype=int)
        lib_dcc     = np.zeros(n_org_codes, dtype=int)

        # Query based on Library patron group for set logic
        faculty_query = ['({})'.format(ual_grouper_base('ual-faculty'))]
        staff_query   = ['({})'.format(ual_grouper_base('ual-staff'))]
        student_query = ['({})'.format(ual_grouper_base('ual-students'))]
        dcc_query     = ['({})'.format(ual_grouper_base('ual-dcc'))]

        faculty_members = ldap_search(lc, faculty_query)
        staff_members   = ldap_search(lc, staff_query)
        student_members = ldap_search(lc, student_query)
        dcc_members     = ldap_search(lc, dcc_query)

        members_list = ['all', 'faculty', 'staff', 'student', 'dcc']
        for org_code, ii in zip(org_codes, range(n_org_codes)):
            # for arr0, member in zip(lib_list, members_list):
            #    query = ual_ldap_query(org_code, members=member)
            #    arr0[ii] = ldap_search(lc, query)

            total_members   = ldap_search(lc, ual_ldap_query(org_code,
                                                             classification='none'))
            library_members = ldap_search(lc, ual_ldap_query(org_code))

            total[ii]       = len(total_members)
            lib_total[ii]   = len(library_members)

            lib_faculty[ii] = len(library_members & faculty_members)
            lib_staff[ii]   = len(library_members & staff_members)
            lib_student[ii] = len(library_members & student_members)
            lib_dcc[ii]     = len(library_members & dcc_members)

        df['total']         = total
        df['pgrps-tot']     = lib_total
        df['pgrps-faculty'] = lib_faculty
        df['pgrps-staff']   = lib_staff
        df['pgrps-student'] = lib_student
        df['pgrps-dcc']     = lib_dcc

        df_sort = df.sort_values(by='Organization Code')
        df_sort.to_csv('org_code_numbers.csv', index=False)

    except URLError:
        print("Unable to retrieve data from URL !")
        print("Please check your internet connection !")
        print("create_csv terminating !")
        raise URLError("Unable to retrieve Google Sheet")

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command-line driver for Organization Code summary information.')
    parser.add_argument('--config', required=True, help='path to configuration file')
    parser.add_argument('--ldap_host', help='LDAP host')
    parser.add_argument('--ldap_base_dn', help='base DN for LDAP bind and query')
    parser.add_argument('--ldap_user', help='user name for LDAP login')
    parser.add_argument('--ldap_password', help='password for LDAP login')
    parser.add_argument('--org_url', help='URL that exports CSV file with organizational code ')
    parser.add_argument('--debug', action='store_true', help='turn on debug logging')
    args = parser.parse_args()

    main_timer = TimerClass()
    main_timer._start()

    config = configparser.ConfigParser()
    config.read(args.config)

    cred_err = 0
    vargs = vars(args)
    for p in ['ldap_host', 'ldap_base_dn', 'ldap_user', 'ldap_password']:

        if (p in vargs) and (vargs[p] is not None):
            vargs[p] = vargs[p]
        elif (p in config['global']) and (config['global'][p] is not None) and \
                (config['global'][p] != "***override***"):
            vargs[p] = config['global'][p]
        else:
            vargs[p] = '(unset)'

        if p in ['ldap_user', 'ldap_password']:
            if vargs[p] is '(unset)':
                print('   {0: >17} = (unset)'.format(p))
                cred_err += 1
            else:
                print('   {0: >17} = (set)'.format(p))
        else:
            print('   {0: >17} = {1:}'. format(p, vargs[p]))

    if cred_err:
        print("Not all credentials available!")
        print("Exiting")
        raise ValueError

    for p in ['org_url']:
        if (p in vargs) and (vargs[p] is not None):
            vargs[p] = vargs[p]
        elif (p in config['org_code']) and (config['org_code'][p] is not None) and \
                (config['org_code'][p] != "***override***"):
            vargs[p] = config['org_code'][p]
        else:
            vargs[p] = '(unset)'

    ldc = LDAPConnection(ldap_host=vargs['ldap_host'],
                         ldap_base_dn=vargs['ldap_base_dn'],
                         ldap_user=vargs['ldap_user'],
                         ldap_password=vargs['ldap_password'])

    get_numbers(ldc, vargs['org_url'])

    print("Completed org_code_numbers successfully!")

    main_timer._stop()
    print(main_timer.format)
