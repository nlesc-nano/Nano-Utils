#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from typing import Dict

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

# To update the package version number, edit nanoutils/__version__.py
version: Dict[str, str] = {}
version_path = os.path.join(here, 'nanoutils', '__version__.py')
with open(version_path, encoding='utf-8') as f:
    exec(f.read(), version)

with open('README.rst', encoding='utf-8') as f:
    readme = f.read()

# Requirements for building the documentation
docs_require = [
    'sphinx>=2.4',
    'sphinx_rtd_theme',
]

# Requirements for building wheels
build_requires = [
    'twine',
    'wheel'
]

# Requirements for running tests
tests_no_optional_require = [
    'assertionlib',
    'mypy>=0.900',
    'pytest>=5.4.0',
    'pytest-cov',
    'pytest-flake8>=1.0.5',
    'pydocstyle>=5.0.0',
    'pytest-pydocstyle>=2.1',
    'pytest-mypy>=0.6.2',
    'types-PyYAML',
]
tests_require = tests_no_optional_require + [
    'schema',
    'pyyaml',
    'h5py',
    'numpy',
]
tests_require += docs_require
tests_require += build_requires

setup(
    name='Nano-Utils',
    version=version['__version__'],
    description='Utility functions used throughout the various nlesc-nano repositories.',
    long_description=f'{readme}\n\n',
    long_description_content_type='text/x-rst',
    author=['Bas van Beek'],
    author_email='b.f.van.beek@vu.nl',
    url='https://github.com/nlesc-nano/Nano-Utils',
    packages=['nanoutils'],
    package_dir={'nanoutils': 'nanoutils'},
    package_data={'nanoutils': ['py.typed', '*.pyi']},
    include_package_data=True,
    license='Apache Software License',
    zip_safe=False,
    keywords=[
        'python-3',
        'python-3-7',
        'python-3-8',
        'python-3-9',
        'libraries'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries',
        'Typing :: Typed'
    ],
    python_requires='>=3.7',
    install_requires=[
        'typing_extensions>=3.10.0; python_version<"3.8"',
    ],
    setup_requires=['pytest-runner'] + docs_require,
    tests_require=tests_require,
    extras_require={
        'doc': docs_require,
        'test': tests_require,
        'test_no_optional': tests_no_optional_require,
        'build': build_requires,
    }
)
