#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from setuptools import setup, find_packages

setup(
    name = 'Dnuos',
    version = '0.95',
    packages = find_packages('src'),
    package_dir = {'': 'src'},

    zip_safe = True,

    # ADD TEST SUITE INFORMATION

    entry_points = {
        'console_scripts': [
            'dnuos = dnuos:main',
        ],
    },

    # Metadata for upload to PyPI
    author = 'Mattias Päivärinta, Brodie Rao',
    author_email = 'pejve@vasteras2.net, me@dackz.net',
    description = 'Dnuos creates lists of your music collection',
    license = 'GNU/GPL',
    keywords = 'music collection list metadata mp3 audiolist oidua',
    url = 'https://dnuos.tweek.us/trac/wiki',
)
