.. image:: https://img.shields.io/pypi/v/fortifyapi.svg
.. image:: https://img.shields.io/pypi/pyversions/fortifyapi.svg
.. image:: https://img.shields.io/circleci/build/github/fortifyadmin/fortifyapi/master?logo=CircleCI

Fortify API
***********

Fortify API is a Python RESTFul API client module for Fortify's `Software Security Center <https://www.microfocus.com/en-us/products/software-security-assurance-sdlc/overview/>`_

Quick Start
~~~~~~~~~~~

Several quick start options are available:

- Build locally: ``pip install wheel setuptools && python setup.py build`` 
- Install with pip (recommended): ``pip install fortifyapi``
- `Download the latest release <https://pypi.org/project/fortifyapi/>`__.

Example
~~~~~~~

.. code:: python

   from os import environ
   from locale import LC_ALL, setlocale
   from fortifyapi.fortify import FortifyApi
    
   # Set encoding
   environ["PYTHONIOENCODING"] = "utf-8"
   myLocale = setlocale(category=LC_ALL, locale="en_GB.UTF-8")
    
   # Set vars for connection
   url = 'https://some-fortify-host/ssc'
   user = 'Fortify SSC User'
   password = 'Fortify SSC Password'
   description = 'fortifyapi test client'
    
   # Authenticate and retrieve token
   def token():
       api = FortifyApi(host=url, username=user, password=password, verify_ssl=False)
       response = api.get_token(description=description)
       return response.data['data']['token']
    
   # Re-use token in all requests
   def api():
       api = FortifyApi(host=url, token=token(), verify_ssl=False)
       return api
    
   # List ID, Project/application Version
   def list():
       response = api().get_all_project_versions()
       data = response.data['data']
       for version in data:
           print("{0:8} {1:30} {2:30}".format(version['id'], version['project']['name'], version['name']).encode(
               'utf-8', errors='ignore').decode())
    
   if __name__ == '__main__':
        list()

Bugs and Feature Requests
~~~~~~~~~~~~~~~~~~~~~~~~~

Found something that doesn't seem right or have a feature request? Please open a new issue.

Copyright and License
~~~~~~~~~~~~~~~~~~~~~
.. image:: https://img.shields.io/github/license/fortifyadmin/fortifyapi.svg?style=flat-square

