Continuous Integration
======================

Initially we started using `Travis CI`_; however, due to the change in
`pricing for open-source repositories`_, we decided to use `GitHub
Actions`_. Currently, there are two GitHub Action workflows:

1. A “Create release” workflow,
   :repo-main-file:`create-release.yml <.github/workflows/create-release.yml>`,
   for new releases when a tag is pushed
2. A “Python package” workflow,
   :repo-main-file:`python-package.yml <.github/workflows/python-package.yml>`,
   for builds and tests

.. _Travis CI: https://travis-ci.com
.. _pricing for open-source repositories:
   https://travis-ci.community/t/org-com-migration-unexpectedly-comes-with-a-plan-change-for-oss-what-exactly-is-the-new-deal/10567
.. _GitHub Actions: https://docs.github.com/en/free-pro-team@latest/actions
