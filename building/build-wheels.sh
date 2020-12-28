#!/bin/bash

# build script for manylinux builder on quay.io/pypa/manylinux2014_x86_64


set -e -u -x


# add builder user and su to build to avoid creating root-owned files in host side.
groupadd --gid $GROUP_ID builder
useradd --no-create-home --comment 'Builder' --uid $USER_ID --gid $GROUP_ID builder

export PYTHONDONTWRITEBYTECODE=1

# Install a system package required by our library
yum install -y zlib-devel
yum install -y openssl-devel

LIBC=$(getconf GNU_LIBC_VERSION | tr -d ' ')


BUILDDIR="/io/build/${LIBC}"

mkdir -p $BUILDDIR
chown -R builder:builder /io/build

pushd $BUILDDIR

su builder -c "\
cmake /io/libssh2 -DBUILD_SHARED_LIBS=ON \
-DENABLE_ZLIB_COMPRESSION=ON -DENABLE_CRYPT_NONE=ON \
-DBUILD_EXAMPLES=OFF -DBUILD_TESTING=OFF \
-DENABLE_MAC_NONE=ON -DCRYPTO_BACKEND=OpenSSL"

su builder -c "cmake --build . --config Release"

popd

# So that loader and auditwheel can find libssh2
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${BUILDDIR}/src

declare -a PYS=(cp36-cp36m cp37-cp37m cp38-cp38 cp39-cp39)

pushd /io

for PY in ${PYS[@]} ; do
    PYBIN=/opt/python/${PY}/bin
    "${PYBIN}/pip" install -U pip setuptools auditwheel
    "${PYBIN}/pip" install -r requirements_dev.txt
    su builder -c "\"${PYBIN}/python\" setup.py bdist_wheel --plat-name $PLAT"
    whl=$(echo dist/*-${PY}-${PLAT}.whl)
    su builder -c "\"${PYBIN}/python\" -m auditwheel repair --plat \"$PLAT\" --wheel-dir /io/wheelhouse/ \"$whl\""
done

popd

echo "Wheels:"
ls -1 /io/wheelhouse/
