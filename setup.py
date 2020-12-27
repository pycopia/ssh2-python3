# python3

import platform
import os
import sys
from glob import glob
from subprocess import check_call
from shutil import copy2

import versioneer
from setuptools import setup, find_packages

from Cython.Distutils.extension import Extension
from Cython.Distutils import build_ext


def build_ssh2():
    if not os.path.exists('build'):
        os.mkdir('build')
    if os.path.exists('build/Makefile'):
        return
    os.chdir('build')
    try:
        check_call('cmake ../libssh2 -DBUILD_SHARED_LIBS=ON \
        -DENABLE_ZLIB_COMPRESSION=ON -DENABLE_CRYPT_NONE=ON \
        -DBUILD_EXAMPLES=OFF -DBUILD_TESTING=OFF \
        -DENABLE_MAC_NONE=ON -DCRYPTO_BACKEND=OpenSSL',
                   shell=True, env=os.environ)
        check_call('cmake --build . --config Release', shell=True, env=os.environ)
    finally:
        os.chdir('..')

    for src in glob('build/src/libssh2.so*'):
        copy2(src, 'ssh2/')


# Only build libssh if running a build
if (len(sys.argv) >= 2 and not (
        '--help' in sys.argv[1:] or
        sys.argv[1] in (
            '--help-commands', 'egg_info', '--version', 'clean',
            'sdist', '--long-description')) and
        __name__ == '__main__'):
    build_ssh2()

sources = glob('ssh2/*.pyx')
_arch = platform.architecture()[0][0:2]
_libs = ['ssh2']

_fwd_default = 0
_comp_args = ["-O3"]
_have_agent_fwd = bool(int(os.environ.get('HAVE_AGENT_FWD', _fwd_default)))

cython_directives = {
    'embedsignature': True,
    'boundscheck': False,
    'optimize.use_switch': True,
    'wraparound': False,
    'language_level': "3",
}

cython_args = {
    'include_path': ["ssh2"],
    'cython_directives': cython_directives,
    'cython_compile_time_env': {
        'EMBEDDED_LIB': True,
        'HAVE_AGENT_FWD': _have_agent_fwd,
    }
}


runtime_library_dirs = ["$ORIGIN/."]
_lib_dir = os.path.abspath("./build/src")
include_dirs = ["libssh2/include"]

extensions = [
    Extension(sources[i].split('.')[0].replace(os.path.sep, '.'),
              sources=[sources[i]],
              include_dirs=include_dirs,
              libraries=_libs,
              library_dirs=[_lib_dir],
              runtime_library_dirs=runtime_library_dirs,
              extra_compile_args=_comp_args,
              **cython_args)
    for i in range(len(sources))]

package_data = {'ssh2': ['*.pxd', 'libssh2.so*']}

cmdclass = versioneer.get_cmdclass()
cmdclass['build_ext'] = build_ext

setup(
    name='ssh2-python3',
    version=versioneer.get_version(),
    cmdclass=cmdclass,
    packages=find_packages(
        '.', exclude=('embedded_server', 'embedded_server.*',
                      'tests', 'tests.*',
                      '*.tests', '*.tests.*')),
    zip_safe=False,
    include_package_data=True,
    tests_require=['pytest'],
    python_requires='~=3.6',
    license='LGPLv2',
    author='Panos Kittenis',
    author_email='22e889d8@opayq.com',
    maintainer='Keith Dart',
    maintainer_email='keith.dart@gmail.com',
    description='Super fast SSH library - bindings for libssh2 and Python 3',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/pycopia/ssh2-python3',
    platforms=['linux_x86_64', 'manylinux2014_x86_64 '],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        "Programming Language :: Python :: 3 :: Only",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: System :: Shells',
        'Topic :: System :: Networking',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: BSD',
    ],
    ext_modules=extensions,
    package_data=package_data,
)
