import os
import sys
import shlex
import subprocess
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages # NOQA

import rmix_api

base_path = os.path.dirname(__file__)
version = rmix_api.__versionstr__

# release a version, publish to GitHub and PyPI
if sys.argv[-1] == 'publish':
    command = lambda cmd: subprocess.check_call(shlex.split(cmd))
    command('git tag v' + version)
    command('git push --tags origin master:master')
    sys.exit()


def read_file(filename):
    return open(os.path.join(base_path, filename)).read()

setup(
    name='rmix_api',
    version=version,
    packages=find_packages(),
    url='http://realitymix.centrum.cz/import/documentation/xml-rpc/',
    license=read_file('LICENSE'),
    author='Martin Voldrich',
    author_email='rbas.cz@gmail.com',
    description='Console API for realitymix.centrum.cz',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
    ),
    entry_points={
        'console_scripts': [
            'rmix_api = rmix_api.console:main',
        ],
    },
)
