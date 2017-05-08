#!/usr/bin/env python
#
# Copyright 2016 Kehr
#
# Licensed under the Apache License, Version 2.0 (the 'License'); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
del os.link
import sys

try:
    from distutils.core import setup
except ImportError:
    from setuptools import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist register upload')
    sys.exit()

setup(
    name='mandb',
    version='0.1.4',
    py_modules=['mandb'],
    author='Kehr',
    author_email='kehr.china@gmail.com',
    url='https://github.com/kehr/mandb',
    license='http://www.apache.org/licenses/LICENSE-2.0',
    description='Mandb is a lightweight wrapper around MySQLdb and sqlite3.',
    keywords=['mysql', 'orm', 'connection pool', 'sqlite', 'torndb', 'database'],
    install_requires=[
        'MySQL-python == 1.2.5'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    )
