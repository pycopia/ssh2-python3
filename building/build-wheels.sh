#!/bin/bash

set -e -u -x

# Install a system package required by our library
yum install -y openssl-devel

for PYBIN in /opt/python/*/bin; do
    "${PYBIN}/pip" install -r /io/requirements-dev.txt
    "${PYBIN}/python" setup.py bdist_wheel
done

# Bundle external shared libraries into the wheels
for whl in dist/*.whl; do
    auditwheel repair "$whl" --plat "$PLAT" -w /io/wheelhouse/
done

ls wheelhouse/
