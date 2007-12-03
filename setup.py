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
    author='Mattias Paivarinta, aiiie',
    author_email='pejve@vasteras2.net; aiiie@aiiie.co',
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
    description='A tool for creating lists of music collections',
    download_url='https://github.com/aiiie/dnuos/archive/refs/tags/1.0b1.tar.gz',
    keywords='music collection list metadata mp3 audiolist oidua',
    license='GNU GPL',
    long_description="""
Dnuos is a console program that creates lists of music collections, based on
directory structure.

For example, a list might look like this::

    Album/Artist                       |  Size | Type | Quality
    ===========================================================
    Ambient                            |       |      | 
        Alva Noto                      |       |      | 
            2001 - Transform           | 70.9M | MP3  | -V2
            2004 - Transrapid          | 30.2M | MP3  | -aps
            2005 - Transspray          | 31.7M | MP3  | -aps
            2005 - Transvision         | 32.3M | MP3  | -aps
        Alva Noto and Ryuichi Sakamoto |       |      | 
            2002 - Vrioon              | 72.6M | MP3  | -aps
            2005 - Insen               | 99.1M | MP3  | 320 C
            2006 - Revep               | 27.9M | MP3  | -V2n

The list format is completely customizable and can be plain text or HTML.

Dnuos supports MP3, AAC, Musepack, OGG Vorbis, and FLAC audio files. Quality
profile detection is also supported, including `LAME quality preset`_
information.

Audio file information is saved to disk after a list is made for the first
time, making subsequent lists much faster to generate. Only audio files and
directories that have been changed since the last list was made are
analyzed.

Dnuos is based on code from Oidua_. Oidua makes similar lists, but is much
older, has fewer features, and is no longer maintained.

.. _LAME quality preset: http://wiki.hydrogenaudio.org/index.php?title=Lame#Recommended_encoder_settings
.. _Oidua: http://oidua.suxbad.com/
""",
    name='Dnuos',
    packages=['dnuos', 'dnuos.id3', 'dnuos.output'],
    url='https://github.com/aiiie/dnuos',
    version='1.0b1',
    **extra_options
)
