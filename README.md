# ![ReDATA EDS Query and Update for Identity and Access Management](ReQUIAM_full.png)

- [Overview](#overview)
- [Getting Started](#getting-started)
    - [Requirements](#requirements)
    - [Installation Instructions](#installation-instructions)
    - [Configuration Settings](#configuration-settings)
    - [Testing Installation](#testing-installation)
- [Execution](#execution)
    - [Manual Changes](#manual-changes)
- [Versioning](#versioning)
- [Changelog](#changelog)
- [Authors](#authors)
- [License](#license)

--------------

## Overview

This identity and access management (IAM) software performs the following for
the [University of Arizona's Research Data Repository (ReDATA)](https://arizona.figshare.com):
 1. It conducts EDS queries to retrieve classification information
    (e.g., student, staff, and/or faculty) and association with
    organization codes (i.e., departments/colleges)
 2. Based on classification information and primary organization
    association, it sets `ismemberof` [Grouper](https://www.incommon.org/software/grouper/) membership

The Grouper memberships are as follow:
 1. The allowed user quota for upload (in bytes), determined by the user's
    classification, is set by Grouper `figshare:quota:<value>` group
 2. The "research theme/portal", determined by the user's organizational
    affiliation, is set by Grouper `figshare:portal:<value>` group

For the latter, these portals and their association with University
organization code(s) are defined within this
[CSV file](https://raw.githubusercontent.com/ualibraries/ReQUIAM_csv/master/requiam_csv/data/research_themes.csv).

Note that access is granted to the service through membership in a Grouper
`figshare:active` group.  These memberships are done indirectly based on
other Grouper membership set forth by University Library privileges.

This software is based on the [existing patron software](https://github.com/ualibraries/patron-groups)
developed for the [University of Arizona Libraries](https://new.library.arizona.edu/).

An illustration of the service architecture workflow is provided below.

# ![ReQUIAM Service Architecture](img/ReQUIAM_architecture.png)

## Getting Started

These instructions will have the code running on your local or virtual machine.


### Requirements

You will need the following to have a working copy of this software. See
[installation](#installation-instructions) steps:
1. Python (3.7.5)
2. [`pandas`](https://pandas.pydata.org/) ([0.25.3](https://pandas.pydata.org/pandas-docs/version/0.25.3/))
3. [`ldap3`](https://ldap3.readthedocs.io/en/latest/) (2.6.1)
4. [`requests`](https://requests.readthedocs.io/en/master/) (2.22.0)
5. [`numpy`](https://numpy.org/doc/) ([1.18.0](https://numpy.org/doc/1.18/))

### Installation Instructions

#### Python and setting up a `conda` environment

First, install a working version of Python (v3.7.5).  We recommend using the
[Anaconda](https://www.anaconda.com/distribution/) package installer.

After you have Anaconda installed, you will want to create a separate `conda` environment
and activate it:

```
$ (sudo) conda create -n figshare_patrons python=3.7.5
$ conda activate figshare_patrons
```

Next, clone this repository into a parent folder:

```
(figshare_patrons) $ cd /path/to/parent/folder
(figshare_patrons) $ git clone https://github.com/ualibraries/ReQUIAM.git
```

With the activated `conda` environment, you can install with the `setup.py` script:

```
(figshare_patrons) $ cd /path/to/parent/folder/ReQUIAM
(figshare_patrons) $ (sudo) python setup.py develop
```

This will automatically installed the required `pandas`, `ldap3`, `requests`, and `numpy` packages.

You can confirm installation via `conda list`

```
(figshare_patrons) $ conda list requiam
```

You should see that the version is `0.11.1`.

### Configuration Settings

Configuration settings are specified through the [config/figshare.ini](config/figshare.ini) file.
The most important settings to set are those populated with `***override***`.
However, for our scripts, these settings can be specified using multi-character 
flag options, such as `--ldap_password`.
Note that most `figshare.ini` settings can be overwritten through the command line.

For manual override (v0.11.0) where IAM portal and quota settings differ from
norm, `config` will include two CSV templates for portal and quota to specify
those changes.


### Testing Installation

To test the installation without performing any `portal` or `quota` query,
execute the following command:

```
(figshare_patrons) $ export password="insert_password"
(figshare_patrons) $ python /path/to/parent/folder/ReQUIAM/scripts/script_run \
                       --config config/figshare.ini \
                       --ldap_password $password --grouper_password $password
```

Test command-line flags (`test` and `test_reverse`) are available to test EDS
query and Grouper synchronization (with the `sync` flag) by executing the following :

```
(figshare_patrons) $ python /path/to/parent/folder/ReQUIAM/scripts/script_run --test \
                       --sync --config config/figshare.ini \
                       --ldap_password $password --grouper_password $password
```

Note that the above will add a test NetID account to the following Grouper
group: `arizona.edu:LBRY:figshare:test`

Without the `sync` flag, the above command line will perform a
"dry run". It will indicate what Grouper updates will occur.

To undo this change, use the `test_reverse` flag:

```
(figshare_patrons) $ python /path/to/parent/folder/ReQUIAM/scripts/script_run \
                       --test_reverse --sync --config config/figshare.ini \
                       --ldap_password $password --grouper_password $password
```

## Execution

To execute the script and update Grouper and EDS, include the `portal`, `quota`,
and `sync` command-line flags:

```
(figshare_patrons) $ python /path/to/parent/folder/ReQUIAM/scripts/script_run \
                       --quota --portal --sync --config config/figshare.ini \
                       --ldap_password $password --grouper_password $password
```

Note: Without the `sync` flag, the above command line will perform a
"dry run" where both `quota` and `portal` queries are conducted. It will
indicate what Grouper updates will occur.


### Manual Changes

While the primary use of this software is automated updates through Grouper,
there are additional scripts for handling.  One of those pertains to overriding
default changes (e.g., a user's quota, involvement with a specific portal).
To this end, the `user_update` script should be used. It has several features:
 1. It can add a given user to a specific group and also remove it from its
    previous group assignment
 2. It will update the appropriate CSV files. This ensures that the changes
    stay when the automated script `script_run` is executed.
 3. It has the ability to move a user to the "main" or "root" portal
 4. It has a number of built-in error handling to identify possible input error.
    This includes:
      a. A username that is not valid
      b. A Grouper group that does not exist
      c. Prevent any action if the user belongs to the specified group

Execution can be done as follows:

```
(figshare_patrons) $ python /path/to/parent/folder/ReQUIAM/scripts/user_update \
                       --netid <username> --config config/figshare.ini \
                       --quota 123456 --portal testportal \
                       --ldap_password $password --grouper_password $password --sync
```

Here, the script will update the specified `<username>` to be associated with
the `123456` quota and the `testportal` portal.  Much like `script_run`,
execution requires the `--sync` flag. Otherwise, a list of changes will be
provided.

To remove a user from its current assignment and place it on the main portal,
use: `--portal root`.

The manual CSV files are specified in the config file:
```python
# Manual override files
portal_file = config/portal_manual.csv
quota_file = config/quota_manual.csv
```

These settings, much like other settings (see `python requiam/user_update --help`),
can be overwritten on the command line:
  ```python
  --portal_file /path/to/portal_manual.csv
  --quota_file /path/to/quota_manual.csv
  ```
Note that working templates are provided in the config folder for
[quota](config/quota_manual_template.csv) and [portal](config/portal_manual_template.csv).


## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the
[tags on this repository](https://github.com/ualibraries/ReQUIAM/tags).


## Changelog

A list of released features and their issue number(s).
List is sorted from moderate to minor revisions for reach release.

v0.11.0 - 0.11.1:
 * Include `manual_override` tool #31, #47
 * Minor: Packaging/re-organization of scripts into `scripts/` #44
 * Minor: Update to scripts

v0.10.0 - 0.10.2:
 * Illustration of software architecture workflow diagram #29
 * Documentation update for configuration settings
 * Bug fix: incorrect URL for `ReQUIAM_csv` #40

v0.9.0 - 0.9.1:
 * Script to determine membership in an organization ("org code") #32
 * Minor: package rename for PEP8

v0.8.0 - 0.8.3:
 * Software renaming #23
 * Minor fixes

v0.7.0:
 * Testing option for `script_run` #18

v0.6.0 - 0.6.1:
 * Primary script for automated patron management #16

v0.5.0 - 0.5.1:
 * Grouper and EDS comparison tool, `Delta` #10, #15

v0.4.0:
 * LDAP quota-based query #4
 * Primary `GrouperQuery` tool #7

v0.3.0:
 * Multi-organization query and LDAP results merge #2

v0.2.0:
 * UA-specific EDS queries

v0.1.0:
 * Initial LDAP query tool and testing


## Authors

* Chun Ly, Ph.D. ([@astrochun](http://www.github.com/astrochun)) - [University of Arizona Libraries](https://github.com/ualibraries), [Office of Digital Innovation and Stewardship](https://github.com/UAL-ODIS)

See also the list of
[contributors](https://github.com/ualibraries/ReQUIAM/contributors) who participated in this project.


## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT) - see the [LICENSE](LICENSE) file for details.
