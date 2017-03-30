#!/usr/bin/env python
#
# Copyright 2016 Kehr
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys

try:
    from distutils.core import setup
except ImportError:
    from setuptools import setup

from mandb import version

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name="mandb",
    version=version,
    py_modules=["mandb"],
    author="Kehr",
    author_email="kehr.china@gmail.com",
    url="https://github.com/kehr/mandb",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="A lightweight wrapper around multiple databases. Database connection pool supported by DBUtils.",
    )
