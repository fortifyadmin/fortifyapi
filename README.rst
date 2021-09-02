.. image:: https://img.shields.io/pypi/v/fortifyapi.svg
   :target: https://pypi.org/project/fortifyapi
.. image:: https://img.shields.io/pypi/pyversions/fortifyapi.svg
.. image:: https://img.shields.io/travis/fortifyadmin/fortifyapi/master.svg
   :target: http://travis-ci.org/fortifyadmin/fortifyapi
   
Fortify API
***********

Fortify API is a Python RESTFul API client module for Fortify's `Software Security Center <https://www.microfocus.com/en-us/products/software-security-assurance-sdlc/overview/>`_

Currently tested fortify version: 20.2.0.298

Quick Start
~~~~~~~~~~~

Several quick start options are available:

- Install with pip (recommended): ``pip install fortifyapi``
- Build locally: ``pip install wheel setuptools && python setup.py build``
- `Download the latest release <https://pypi.org/project/fortifyapi/>`__.

Example
~~~~~~~

.. code:: python

    import os
    from fortifyapi import FortifySSCClient

    ssc_url = "https://fortifyssc.prodsec.dev/ssc"

    # make the client with a token
    client = FortifySSCClient(ssc_url, os.environ['TOKEN'])

    # or make a client using user/pass auth (not recommended for automation tasks)
    client = FortifySSCClient(ssc_url, (os.environ['USER'], os.environ['PASSW']))


    # List ID, Project/application Version
    for project in client.projects.list():
        for version in project.versions.list():
            print(f"Found version {version['name']} in project {project['name']}")

    # Or query for all versions named 'default'
    for version in project.versions.list(q=Query().query('name', 'default')):
        print(f"Found version {version['name']} in project {project['name']}")
        # and get the issue summary
        summary = version.issue_summary()


Bugs and Feature Requests
~~~~~~~~~~~~~~~~~~~~~~~~~

Found something that doesn't seem right or have a feature request? Please open a new issue.

Copyright and License
~~~~~~~~~~~~~~~~~~~~~
.. image:: https://img.shields.io/github/license/fortifyadmin/fortifyapi.svg?style=flat-square

