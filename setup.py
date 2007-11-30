#!/usr/bin/env python

import os

try:
    from setuptools import setup
    extra_options = dict(
        entry_points={'console_scripts': ['dnuos = dnuos:main']},
        tests_require=['nose >= 0.9'],
        test_suite='nose.collector',
    )
    os.environ['DATA_DIR'] = os.environ.get(
        'DATA_DIR',
        os.path.abspath('./testdata')
    )
except ImportError:
    from distutils.core import setup
    extra_options = dict(
        scripts=['scripts/dnuos'],
    )

setup(
    author='Mattias P\xc3\xa4iv\xc3\xa4rinta, aiiie',
    author_email=('Mattias P\xc3\xa4iv\xc3\xa4rinta <pejve@vasteras2.net>;'
                  ' "aiiie" <aiiie@aiiie.co>'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Communications :: File Sharing',
        'Topic :: Multimedia :: Sound/Audio',
    ],
    description='Dnuos creates lists of your music collection',
    keywords='music collection list metadata mp3 audiolist oidua',
    license='GNU GPL',
    name='Dnuos',
    packages=['dnuos', 'dnuos.id3', 'dnuos.output'],
    url='https://https://github.com/aiiie/dnuos/',
    version='1.0b0',
    **extra_options
)
