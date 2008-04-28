#!/usr/bin/env python

try:
    from setuptools import setup, Command
    from setuptools.command.build_py import build_py
    extra_options = dict(
        entry_points={'console_scripts': ['dnuos = dnuos:main']},
        zip_safe=True,
    )
except ImportError:
    from distutils.core import setup, Command
    from distutils.command.build_py import build_py
    extra_options = dict(
        scripts=['scripts/dnuos'],
    )

package_data = {'dnuos': ['locale/*/LC_MESSAGES/*.mo']}

try:
    import py2exe
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'py2exe':
        sys.argv.extend(('-O2 -c -b 1 -e _ssl,calendar,doctest,email,ftplib,'
                         'getpass,gettext,gopherlib,httplib,mimetypes,'
                         'quopri,unittest -i dbhash -p bsddb').split(' '))
        package_data = {}
    extra_options.update(dict(
        console=['scripts/dnuos'],
    ))
except ImportError:
    pass


class LocaleBuildPy(build_py):
    """Build locale data automatically"""

    def run(self):

        from glob import glob
        from msgfmt import compile_catalog
        for path in glob('./dnuos/locale/*/LC_MESSAGES/*.po'):
            compile_catalog(path)
        return build_py.run(self)


def testpkg(path):
    """Runs doctest on an entire package"""

    import doctest
    import os
    from glob import glob
    modules = glob(os.path.join(path, '*.py'))
    modules += glob(os.path.join(path, '**/*.py'))
    total_failures, total_tests = 0, 0
    for module in modules:
        if module.endswith('__init__.py'):
            continue
            module = module[:-len(os.path.sep + '__init__.py')]
        module = os.path.splitext(module)[0]
        module = module.replace(os.path.sep, '.')
        justmodule = module.split('.', 1)[1]
        failures, tests = doctest.testmod(__import__(module, {}, {}, [justmodule]))
        if tests > 0:
            print '%s: %s/%s passed' % (module, tests + (0 - failures), tests)
        total_failures += failures
        total_tests += tests

    print 'Total: %s/%s passed' % (total_tests + (0 - total_failures), total_tests)
    print ''


class RunTests(Command):
    """Runs test suite"""

    description = 'Runs test suite'
    user_options = [
        ('data-dir=', 'd', 'path to test data [default: ./testdata]'),
    ]

    def initialize_options(self):
        import os
        self.data_dir = os.path.abspath('./testdata')

    def finalize_options(self):
        import os
        os.environ['DATA_DIR'] = self.data_dir

    def run(self):

        testpkg('dnuos')
        testpkg('dnuostests')


setup(
    author='Mattias P\xc3\xa4iv\xc3\xa4rinta, Brodie Rao',
    author_email='pejve@vasteras2.net; me+dnuos@dackz.net',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Natural Language :: French',
        'Operating System :: OS Independent',
        'Topic :: Communications :: File Sharing',
        'Topic :: Multimedia :: Sound/Audio',
    ],
    cmdclass={'build_py': LocaleBuildPy, 'test': RunTests},
    description='A tool for creating lists of music collections',
    download_url='http://dnuos.tweek.us/files/dnuos-1.0.3.tar.gz',
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

Dnuos supports MP3, AAC, Musepack, Ogg Vorbis, and FLAC audio files. Quality
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
    name='dnuos',
    packages=['dnuos', 'dnuos.id3', 'dnuos.output'],
    package_data=package_data,
    url='http://dnuos.tweek.us/',
    version='1.0.3',
    **extra_options
)
