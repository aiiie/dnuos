#!/usr/bin/env python

import os

from setuptools import setup, find_packages

os.environ['DATA_DIR'] = './testdata'

setup(
    author='Mattias Paivarinta, Brodie Rao',
    author_email='pejve@vasteras2.net, me+dnuos@dackz.net',
    description='Dnuos creates lists of your music collection',
    entry_points={'console_scripts': ['dnuos = dnuos:main']},
    keywords='music collection list metadata mp3 audiolist oidua',
    license='GNU/GPL',
    name='Dnuos',
    packages=find_packages(exclude=['dnuostests']),
    tests_require=['nose >= 0.9'],
    test_suite='nose.collector',
    url='https://dnuos.tweek.us/trac/wiki',
    version='1.0',
    zip_safe=True,
)
