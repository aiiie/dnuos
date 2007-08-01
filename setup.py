#!/usr/bin/env python

import os

from setuptools import setup, find_packages

os.environ['DATA_DIR'] = os.environ.get(
    'DATA_DIR',
    os.path.abspath('./testdata')
)

setup(
    author='Mattias Paivarinta, aiiie',
    author_email='pejve@vasteras2.net, aiiie@aiiie.co',
    description='Dnuos creates lists of your music collection',
    entry_points={'console_scripts': ['dnuos = dnuos:main']},
    keywords='music collection list metadata mp3 audiolist oidua',
    license='GNU/GPL',
    name='Dnuos',
    packages=find_packages(exclude=['dnuostests']),
    tests_require=['nose >= 0.9'],
    test_suite='nose.collector',
    url='https://https://github.com/aiiie/dnuos/trac/wiki',
    version='1.0',
    zip_safe=True,
)
