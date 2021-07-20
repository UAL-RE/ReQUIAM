Overview
========

This identity and access management (IAM) software performs the following
for the `University of Arizona’s Research Data Repository (ReDATA)`_:

1. It conducts EDS queries to retrieve classification information (e.g.,
   student, staff, and/or faculty) and association with organization codes
   (i.e., departments/colleges)
2. Based on classification information and primary organization association,
   it sets ``ismemberof`` `Grouper`_ membership

The Grouper memberships are as follow:

1. The allowed user quota for upload (in bytes), determined by the user’s
   classification, is set by Grouper ``figshare:quota:<value>`` group
2. The “research theme/portal”, determined by the user’s organizational
   affiliation, is set by Grouper ``figshare:portal:<value>`` group

For the latter, these portals and their association with University
organization code(s) are defined within this `CSV file`_.

Note that access is granted to the service through membership in a Grouper
``figshare:active`` group. These memberships are done indirectly based on
other Grouper membership set forth by University Library privileges.

This software is based on the `existing patron software`_ developed for the
`University of Arizona Libraries`_.

An illustration of the service architecture workflow is provided below.

.. image:: ../../img/ReQUIAM_architecture.png


.. _University of Arizona’s Research Data Repository (ReDATA): https://arizona.figshare.com
.. _Grouper: https://www.incommon.org/software/grouper/
.. _CSV file: https://raw.githubusercontent.com/UAL-RE/ReQUIAM_csv/master/requiam_csv/data/research_themes.csv
.. _existing patron software: https://github.com/ualibraries/patron-groups
.. _University of Arizona Libraries: https://new.library.arizona.edu/
