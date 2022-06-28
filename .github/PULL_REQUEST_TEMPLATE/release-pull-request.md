---
name: Release
about: Provide specifics about a PR for a release
title: 'PR/Release: ____(provide a descriptive name)'
assignees: ''

---
<!-- IMPORTANT: Please do not create a PR without creating an issue first. -->

<!-- Fields in **bold** are REQUIRED, fields in *italics* are OPTIONAL. -->

**Description**
<!-- A description of the updates contained in this release. Example:  -->

Closes #


**Update Changelog**
<!-- List changes: be brief, use imperative mood or simple noun phrases and add linked issues -->
<!-- Examples: Improve verbosity of log messages #103 | GitHub actions for CI #105 -->

- [ ] [changelog](../../CHANGELOG.md) <!-- update changelog here -->

**Bump version**

v0.xx.x -> v0.xx.0

- [ ] [README.md](../../README.md) (if needed)
- [ ] [`setup.py`](../../setup.py)
- [ ] [`requiam/__init__.py`](../../requiam/__init__.py)
- [ ] ReadTheDocs [`conf.py`](../../docs/source/conf.py)
- [ ] ReadTheDocs [`conf.py`](../../docs/source/getting_started.rst)

**Update Additional Documentation**
- [ ] [ReadTheDocs files](../../docs/source/). Check and update the appropriate sections as needed

*Screenshots or additional context*
<!-- Add any other context about this release. -->

<!-- Do not push the release tag until this PR is merged -->
