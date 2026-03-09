
import os
from glob import glob

from setuptools import setup, find_packages

from Cython.Distutils.extension import Extension
from Cython.Distutils import build_ext


LIBC = os.confstr('CS_GNU_LIBC_VERSION')
assert LIBC is not None
LIBC = LIBC.replace(" ", "")

sources = glob('ssh2/*.pyx')
_libs = ['ssh2', 'ssl', 'crypto', 'z']

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


_lib_dir = os.path.abspath(f"./build/{LIBC}/src")
include_dirs = ["libssh2/include"]

extensions = [
    Extension(pyx.split('.')[0].replace(os.path.sep, '.'),
              sources=[pyx],
              include_dirs=include_dirs,
              libraries=_libs,
              library_dirs=[_lib_dir],
              extra_compile_args=_comp_args,
              **cython_args)
    for pyx in sources]

package_data = {'ssh2': ['*.pxd']}


setup(
    name='ssh2-python3',
    cmdclass={"build_ext": build_ext},
    packages=find_packages(
        '.', exclude=('embedded_server', 'embedded_server.*',
                      'tests', 'tests.*',
                      '*.tests', '*.tests.*')),
    zip_safe=False,
    include_package_data=True,
    tests_require=['pytest'],
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    platforms=['linux_x86_64', 'manylinux_2_35_x86_64'],
    ext_modules=extensions,
    package_data=package_data,
)
