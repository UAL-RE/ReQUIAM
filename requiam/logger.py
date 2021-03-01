import sys
import io
from os.path import join, dirname
from os import uname, chmod

import logging

# User and hostname
from getpass import getuser
from socket import gethostname
from requests import get

from .git_info import get_active_branch_name, get_latest_commit
from requiam import __file__ as library_path, __version__

library_root_path = dirname(dirname(library_path))  # Retrieve parent directory to requiam

formatter = logging.Formatter('%(asctime)s - %(levelname)8s: %(message)s', "%H:%M:%S")

file_formatter = logging.Formatter('%(asctime)s %(levelname)8s - %(module)20s %(funcName)30s : %(message)s',
                                   "%H:%M:%S")


class LogClass:
    """
    Purpose:
      Main class to log information to stdout and ASCII logfile

    Note: This code is identical to the one used in DataRepository_research_themes:
      https://github.com/ualibraries/DataRepository_research_themes

    To use:
    log = LogClass(log_dir, logfile).get_logger()

    Parameters:
      log_dir: Relative path for exported logfile directory
      logfile: Filename for exported log file
    """

    def __init__(self, log_dir, logfile):
        self.LOG_FILENAME = join(log_dir, logfile)

    def get_logger(self):
        file_log_level = logging.DEBUG  # This is for file logging
        log = logging.getLogger("main_logger")
        if not log.handlers:
            log.setLevel(file_log_level)

            sh = logging.StreamHandler(sys.stdout)
            sh.setLevel(logging.INFO)  # Only at INFO level
            sh.setFormatter(formatter)
            log.addHandler(sh)

            fh = logging.FileHandler(self.LOG_FILENAME)
            fh.setLevel(file_log_level)
            fh.setFormatter(file_formatter)
            log.addHandler(fh)

            log.handler_set = True
            log.propagate = False
        return log


def log_stdout():
    log_level = logging.INFO
    log = logging.getLogger("stdout_logger")
    if not log.handlers:
        log.setLevel(log_level)
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(formatter)
        log.addHandler(sh)

        log.handler_set = True
        log.propagate = False
    return log


def get_user_hostname():
    """
    Purpose:
      Retrieve user, hostname, IP, and OS configuration
    :return sys_info: dictionary with 'user' 'hostname' and 'ip' dictionary
    """

    sys_info = dict()

    sys_info['user'] = getuser()
    sys_info['hostname'] = gethostname()
    sys_info['ip'] = get('https://api.ipify.org').text

    os_name = uname()
    sys_info['os'] = f"{os_name[0]} {os_name[2]} {os_name[3]}"

    return sys_info


class LogCommons:
    def __init__(self, log: logging.Logger):
        self.log = log
        self.sys_info = get_user_hostname()

    def script_start(self, script_name: str, branch_name: str,
                     git_short_commit: str, git_commit: str):
        start_text = f"Started {script_name} script ... "
        self.log.info(f"*"*len(start_text))
        self.log.info(start_text)
        self.log.debug(f"ReQUIAM active branch: {branch_name}")
        self.log.debug(f"ReQUIAM version: {__version__} ({git_short_commit})")
        self.log.debug(f"ReQUIAM commit hash: {git_commit}")

    def script_sys_info(self):
        self.log.debug(f"username : {self.sys_info['user']}")
        self.log.debug(f"hostname : {self.sys_info['hostname']}")
        self.log.debug(f"IP Addr  : {self.sys_info['ip']}")
        self.log.debug(f"Op. Sys. : {self.sys_info['os']}")

    def script_end(self):
        self.log.info("******************************")
        self.log.info("Exit 0")

    def log_permission(self, log_file):
        self.log.debug(f"Changing permissions for {log_file}")
        chmod(log_file, mode=0o666)


def pandas_write_buffer(df, log_filename):
    """
    Purpose:
      Write pandas content via to_markdown() to logfile

    :param df: pandas DataFrame
    :param log_filename: Full path for log file
    """

    buffer = io.StringIO()
    df.to_markdown(buffer)
    print(buffer.getvalue())

    with open(log_filename, mode='a') as f:
        print(buffer.getvalue(), file=f)
    buffer.close()


def log_settings(vargs, config_dict, protected_keys, log=None):
    """
    Purpose:
      Log parsed arguments settings for scripts

    :param vargs: dict of parsed arguments
    :param config_dict: dict containing configuration settings. See commons.dict_load
    :param protected_keys: list of private arguments to print unset or set status
    :param log: LogClass

    :return cred_error: int providing number of errors with credentials
    """

    if log is None:
        log = log_stdout()

    cred_err = 0
    sections = config_dict.keys()
    for p in vargs.keys():
        value = ''
        for section in sections:
            if p in config_dict[section].keys():
                value = config_dict[section][p]

        if p in protected_keys:
            if value == '***override***' or value == '':
                log.info(f'   {p: >17} = (unset)')
                cred_err += 1
            else:
                log.info(f'   {p: >17} = (set)')
        else:
            log.info(f"   {p: >17} = {value}")

    return cred_err
