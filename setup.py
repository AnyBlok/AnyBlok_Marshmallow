#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok / Marshmallow api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.

from setuptools import setup, find_packages
from os.path import abspath, dirname, join


version = "2.2.3"
here = abspath(dirname(__file__))

with open(join(here, 'README.rst'), 'r',
          encoding='utf-8') as readme:
    README = readme.read()

with open(
    join(here, 'doc', 'MEMENTO.rst'), 'r', encoding='utf-8'
) as memento:
    MEMENTO = memento.read()

with open(
    join(here, 'doc', 'CHANGES.rst'), 'r', encoding='utf-8'
) as change:
    CHANGE = change.read()

with open(
    join(here, 'doc', 'FRONT.rst'), 'r', encoding='utf-8'
) as front:
    FRONT = front.read()


requirements = [
    'anyblok',
    'marshmallow>=3.2.1',
    'marshmallow-sqlalchemy>=0.19.0',
]

setup(
    name='anyblok_marshmallow',
    version=version,
    description="Add validator, serializer and deserializer to AnyBlok",
    long_description=README + '\n' + FRONT + '\n' + MEMENTO + '\n' + CHANGE,
    author="Jean-Sébastien SUZANNE",
    author_email='jssuzanne@anybox.fr',
    url='https://anyblok-marshmallow.readthedocs.io/en/' + version,
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='anyblok_marshmallow',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
    ],
)
