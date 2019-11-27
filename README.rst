.. image:: https://img.shields.io/pypi/v/fortifyapi.svg
   :target: https://pypi.org/project/fortifyapi
.. image:: https://img.shields.io/pypi/pyversions/fortifyapi.svg
.. image:: https://img.shields.io/travis/fortifyadmin/fortifyapi/master.svg
   :target: http://travis-ci.org/fortifyadmin/fortifyapi
   
Fortify API
***********

Fortify API is a Python RESTFul API client module for Fortify's `Software Security Center <https://www.microfocus.com/en-us/products/software-security-assurance-sdlc/overview/>`_

Quick Start
~~~~~~~~~~~

Several quick start options are available:

- Build locally: ``pip install wheel setuptools && python setup.py build`` 
- Install with pip (recommended): ``pip install fortifyapi``
- `Download the latest release <https://github.com/fortifyadmin/fortifyapi/releases/latest/>`__.

Example
~~~~~~~

::

    # import the package
    from fortifyapi import fortify

    # setup fortify ssc connection information
    host = 'https://localhost:8443/'

    # instantiate the fortify api wrapper
    ssc = fortify.FortifyApi(host)

    # Do something

Supporting information for each method available can be found in the `documentation <https://fortifyadmin.github.io/fortifyapi/>`__.

Bugs and Feature Requests
~~~~~~~~~~~~~~~~~~~~~~~~~

Found something that doesn't seem right or have a feature request? Please open a new issue.

Copyright and License
~~~~~~~~~~~~~~~~~~~~~
.. image:: https://img.shields.io/github/license/fortifyadmin/fortifyapi.svg?style=flat-square

