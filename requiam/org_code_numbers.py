from logging import Logger

# For database/CSV
import pandas as pd
import numpy as np
from urllib.error import URLError

# For LDAP query
from .ldap_query import LDAPConnection, ual_grouper_base, ual_ldap_query, ldap_search

from datetime import date

today = date.today()


def get_numbers(lc: LDAPConnection, org_url: str, log: Logger) -> None:
    """
    Determine number of individuals in each organization code with
    Library privileges and write to a file called "org_code_numbers.csv"

    :param lc: LDAPConnection object for EDS record retrieval
    :param org_url: Google Docs URL that provides CSV
    :param log: File and/or stdout logging class

    :raises URLError: Incorrect ``org_url``
    """

    try:
        df = pd.read_csv(org_url)

        n_org_codes = df.shape[0]
        log.info(f"Number of organizational codes : {n_org_codes}")

        org_codes = df['Organization Code'].values

        # Arrays for members with library privileges based on classification
        total       = np.zeros(n_org_codes, dtype=int)
        lib_total   = np.zeros(n_org_codes, dtype=int)
        lib_faculty = np.zeros(n_org_codes, dtype=int)
        lib_staff   = np.zeros(n_org_codes, dtype=int)
        lib_student = np.zeros(n_org_codes, dtype=int)
        lib_dcc     = np.zeros(n_org_codes, dtype=int)

        # Query based on Library patron group for set logic
        faculty_query = [f"({ual_grouper_base('ual-faculty')})"]
        staff_query   = [f"({ual_grouper_base('ual-staff')})"]
        student_query = [f"({ual_grouper_base('ual-students')})"]
        dcc_query     = [f"({ual_grouper_base('ual-dcc')})"]

        log.info("Getting faculty, staff, student, and dcc members ... ")
        faculty_members = ldap_search(lc, faculty_query)
        staff_members   = ldap_search(lc, staff_query)
        student_members = ldap_search(lc, student_query)
        dcc_members     = ldap_search(lc, dcc_query)
        log.info("Completed faculty, staff, student, and dcc queries")

        for org_code, ii in zip(org_codes, range(n_org_codes)):

            if ii % round(n_org_codes/10) == 0 or ii == n_org_codes-1:
                log.info(f"{round((ii + 1) / n_org_codes * 100): >3}% completed ...")

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
        log.info("Unable to retrieve data from URL !")
        log.info("Please check your internet connection !")
        log.info("create_csv terminating !")
        raise URLError("Unable to retrieve Google Sheet")
