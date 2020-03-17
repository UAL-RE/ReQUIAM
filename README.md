# DataRepository_patrons

- [Overview](#overview)
- [Getting Started](#getting-started)
    - [Requirements](#requirements)
    - [Installation Instructions](#installation-instructions)
    - [Testing Installation](#testing-installation)
- [Execution](#execution)
- [Versioning](#versioning)
- [Authors](#authors)
- [License](#license)

--------------

## Overview

This identity and access management (IAM) software performs the following for
the [University of Arizona's Figshare data repository](https://arizona.figshare.com):
 1. It conducts EDS queries to retrieve classification information
    (e.g., student, staff, and/or faculty) and association with
    organization codes (i.e., departments)
 2. Based on classification information and primary organization
    association, it sets `ismemberof` [Grouper](https://www.incommon.org/software/grouper/) membership

The Grouper memberships are as follow:
 1. The allowed user quota for upload, determined by the user's classification,
    is set by Grouper `figshare:quota:<value>` group.
 2. The "research theme/portal", determined by the user's organizational
    affiliation, is set by Grouper `figshare:portal:<value>` group.

For the latter, these portals and their association with University
organization code(s) are defined within this
[CSV file](https://raw.githubusercontent.com/ualibraries/DataRepository_research_themes/master/DataRepository_research_themes/data/research_themes.csv).

Note that access is granted to the service through membership in a Grouper
`figshare:active` group.  These memberships are done indirectly based on
other Grouper membership set forth by University Library privileges.

This software is based on the [existing patron software](https://github.com/ualibraries/patron-groups)
developed for the [University of Arizona Libraries](https://new.library.arizona.edu/).

## Getting Started

These instructions will have the code running on your local or virtual machine.


### Requirements

You will need the following to have a working copy of this software. See
[installation](#installation-instructions) steps:
1. Python (3.7.5)
2. [`pandas`](https://pandas.pydata.org/) ([0.25.3](https://pandas.pydata.org/pandas-docs/version/0.25.3/))
3. [`ldap3`](https://ldap3.readthedocs.io/en/latest/) (2.6.1)
4. [`requests`](https://requests.readthedocs.io/en/master/) (2.22.0)


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
(figshare_patrons) $ git clone https://github.com/ualibraries/DataRepository_patrons.git
```

With the activated `conda` environment, you can install with the `setup.py` script:

```
(figshare_patrons) $ cd /path/to/parent/folder/DataRepository_patrons
(figshare_patrons) $ (sudo) python setup.py develop
```

This will automatically installed the required `pandas`, `ldap3`, and `requests` packages.

You can confirm installation via `conda list`

```
(figshare_patrons) $ conda list datarepository-patrons
```

You should see that the version is `0.6.0`.


### Testing Installation

To test the installation without performing the Grouper synchronization,
execute the following command:

```
(figshare_patrons) $ export password="insert_password"
(figshare_patrons) $ python DataRepository_patrons/script_run --config config/figshare.ini \
                       --ldap_password $password --grouper_password $password
```


## Execution

To execute the script and update Grouper and EDS, include the `portal`, `quota`,
and `sync` command-line flags:

```
(figshare_patrons) $ python DataRepository_patrons/script_run --quota --portal --sync \
                       --config config/figshare.ini --ldap_password $password --grouper_password $password
```

Note: Without the `sync` flag, the above command line will perform a
"dry run" where both `quota` and `portal` queries are conducted. It will
indicate what Grouper updates will occur.


## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the
[tags on this repository](https://github.com/ualibraries/DataRepository_patrons/tags).


## Authors

* Chun Ly, Ph.D. ([@astrochun](http://www.github.com/astrochun)) - [University of Arizona Libraries](https://github.com/ualibraries), [Office of Digital Innovation and Stewardship](https://github.com/UAL-ODIS)

See also the list of
[contributors](https://github.com/ualibraries/DataRepository_patrons/contributors) who participated in this project.


## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT) - see the [LICENSE](LICENSE) file for details.
