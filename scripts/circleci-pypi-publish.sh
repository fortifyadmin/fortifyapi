#!/bin/sh

set -e

PYPI_CONFIG="${HOME}/.pypirc"
pip install --upgrade  pip
pip install --upgrade packaging # See https://github.com/pypa/twine/issues/1216
pip install twine
echo "[distutils]\nindex-servers = pypi\n[pypi]" > $PYPI_CONFIG
echo "username=$PYPI_USERNAME" >> $PYPI_CONFIG
echo "password=$PYPI_PASSWORD" >> $PYPI_CONFIG
twine upload dist/*
