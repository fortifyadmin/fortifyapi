#!/usr/bin/env python

import os
import sys

from fortifyapi import __version__ as version

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst', 'r') as f:
    readme = f.read()

# Publish helper
if sys.argv[-1] == 'build':
    os.system('python setup.py sdist bdist')
    sys.exit(0)

if sys.argv[-1] == 'tag':
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit(0)

if sys.argv[-1] == 'publish-test':
    os.system('python setup.py sdist bdist_wheel upload -r pypitest')
    sys.exit(0)

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    sys.exit()

setup(
    name='fortifyapi',
    packages=['fortifyapi'],
    version=version,
    description='Python library for Fortify Software Security Center (SSC) RESTFul API',
    long_description=readme,
    long_description_content_type = "text/x-rst",
    author='Brandon Spruth, Matthew Gill',
    author_email='brandon@spruth.co, mgill@c0ffee.me',
    url='https://github.com/fortifyadmin/fortifyapi',
    download_url='https://github.com/fortifyadmin/fortifyapi/tarball/' + version,
    license='MIT',
    zip_safe=True,
    test_suite='nose.collector',
    tests_require=['nose'],
    requires=['requests'],
    install_requires=['requests'],
    keywords=['fortify', 'api', 'security', 'software', 'microfocus', 'ssc', 'sast'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
