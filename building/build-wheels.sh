#!/bin/bash

# build script for building manylinux wheels.


set -e -u -x


# add builder user and su to build to avoid creating root-owned files in host side.
groupadd --gid $GROUP_ID builder
useradd --no-create-home --comment 'Builder' --uid $USER_ID --gid $GROUP_ID builder
git config --global --add safe.directory /io

# apt install -y libssl-dev
# apt install -y zlib1g-dev

export PYTHONDONTWRITEBYTECODE=1

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
export LD_LIBRARY_PATH=${BUILDDIR}/src


declare -a PYTHONS=(cp37-cp37m cp38-cp38 cp39-cp39 cp310-cp310 cp311-cp311)

pushd /io

for PY in ${PYTHONS[@]} ; do
    PYBIN=/opt/python/${PY}/bin
    "${PYBIN}/pip" install -r requirements_dev.txt
    rm -f ssh2/*.c
    su builder -c "\"${PYBIN}/python\" setup.py bdist_wheel --plat-name $PLAT"
    whl=$(echo dist/*-${PY}-${PLAT}.whl)
    su builder -c "\"${PYBIN}/python\" -m auditwheel repair --plat \"$PLAT\" --wheel-dir /io/wheelhouse/ \"$whl\""
done

popd

echo "Wheels:"
ls -1 /io/wheelhouse/
