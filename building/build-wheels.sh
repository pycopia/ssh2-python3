#!/bin/bash

set -e -u -x

cd /io

groupadd --gid $GROUP_ID builder
useradd --no-create-home --comment 'Builder' --uid $USER_ID --gid $GROUP_ID builder

export PYTHONDONTWRITEBYTECODE=1

# Install a system package required by our library
yum install -y openssl-devel

for PYBIN in /opt/python/*/bin; do
    "${PYBIN}/pip" install -U pip setuptools
    "${PYBIN}/pip" install -r requirements_dev.txt
    su builder -c "\"${PYBIN}/python\" setup.py bdist_wheel"
done

# Bundle external shared libraries into the wheels
for whl in dist/*.whl; do
    su builder -c "auditwheel repair \"$whl\" --plat \"$PLAT\" -w /io/wheelhouse/"
done

ls wheelhouse/
