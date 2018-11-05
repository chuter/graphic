#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


DESCRIPTION = 'More phthonic, humanize way to play with graphdb'
URL = 'https://github.com/chuter/graphic'
EMAIL = 'topgun.chuter@gmail.com'
AUTHOR = 'chuter'
VERSION = None

# What packages are required for this module to be executed?
REQUIRED = [
    'six',
]

TEST_REQUIREMENTS = [
    'pytest-cov',
    'pytest-mock',
    'pytest-xdist',
    'pytest>=2.8.0'
]

here = os.path.abspath(os.path.dirname(__file__))
src = os.path.join(here, 'src')


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass into py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        try:
            from multiprocessing import cpu_count
            self.pytest_args = ['-n', str(cpu_count())]
        except (ImportError, NotImplementedError):
            self.pytest_args = ['-n', '1']

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist')
    os.system('twine upload dist/*')
    sys.exit()

with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()


meta = {}
if VERSION is None:
    with open(os.path.join(src, 'graphic', 'meta.py')) as f:
        exec(f.read(), meta)
else:
    meta['__version__'] = VERSION


setup(
    name=meta['__name__'],
    version=meta['__version__'],
    description=DESCRIPTION,
    license='MIT',
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=">=3.5",
    url=URL,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=REQUIRED,
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: Chinese (Simplified)',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    keywords=[
        'graph', 'neo4j', 'graph algorithms', 'client'
    ],
    cmdclass={'test': PyTest},
    tests_require=TEST_REQUIREMENTS,
    setup_requires=['pytest-runner'],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
)
