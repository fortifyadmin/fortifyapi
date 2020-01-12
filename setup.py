#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = "(C) 2019 Brandon Spruth"
__status__ = "Planning"
__license__ = "MIT"
__since__ = "0.0.1"

import sys
import os
from fortifyadmin.__init__ import __version__ as version
from setuptools import setup, find_packages

try:
    from pip._internal.req import parse_requirements
    from pip._internal.download import PipSession
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements
    from pip.download import PipSession

links = []
requires = []

if os.path.isfile('requirements.txt'):
    requirements = parse_requirements('requirements.txt',
                                      session=PipSession())
    for item in requirements:
        if getattr(item, 'url', None):
            links.append(str(item.url))
        if getattr(item, 'link', None):
            links.append(str(item.link))
        if item.req:
            requires.append(str(item.req))

# run pyinstaller
if sys.argv[-1] == 'pyinstaller':
    os.system('python build.py')
    sys.exit(0)

if sys.argv[-1] == 'build':
    os.system('python setup.py sdist --formats=zip bdist_wheel')
    sys.exit(0)

setup(
    author='Brandon Spruth',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 1 - Planning',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation ::CPython'],
    description='JIRA client to maintain issue_tracking state',
    entry_points={
        'console_scripts': [
            'fortifyadmin= fortifyadmin.__main__:cli',
        ],
    },
    include_package_data=True,
    install_requires=requires,
    dependency_links=links,
    license='MIT',
    long_description='Command line client for Fortify SSC Orchestration',
    name='fortifyadmin',
    packages=find_packages(exclude=['docs', 'images', 'tests*']),
    tests_require=['pytest'],
    url="https://www.servicenow.com",
    version=version,
)
