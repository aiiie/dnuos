#!/usr/bin/env python

from distutils.core import setup, Command

# This is absolutely ridiculous.
from distutils.dist import Distribution
if Distribution.__module__.startswith('setuptools.'):
    from setuptools.command.build_py import build_py as old_build_py
    from setuptools.command.install import install as old_install
else:
    from distutils.command.build_py import build_py as old_build_py
    from distutils.command.install import install as old_install

extra_options = {}
package_data = {'dnuos': ['locale/*/LC_MESSAGES/*.mo']}

try:
    import py2exe
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'py2exe':
        sys.argv.extend(('-O2 -c -b 1 -e _ssl,calendar,doctest,email,ftplib,'
                         'getpass,gettext,gopherlib,httplib,mimetypes,'
                         'quopri,unittest').split(' '))
        package_data = {}
    extra_options.update(dict(
        console=['scripts/dnuos'],
    ))
except ImportError:
    pass


class build_py(old_build_py):
    """Builds locale data automatically"""

    def run(self):
        from glob import glob
        from msgfmt import compile_catalog
        for path in glob('./dnuos/locale/*/LC_MESSAGES/*.po'):
            compile_catalog(path)
        old_build_py.run(self)


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
        module = os.path.splitext(module)[0]
        module = module.replace(os.path.sep, '.')
        justmodule = module.split('.', 1)[1]
        failures, tests = doctest.testmod(__import__(module, {}, {},
                                                     [justmodule]))
        if tests > 0:
            print '%s: %s/%s passed' % (module, tests + (0 - failures), tests)
        total_failures += failures
        total_tests += tests

    print 'Total: %s/%s passed' % (total_tests + (0 - total_failures),
                                   total_tests)
    print ''


class test(Command):
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


class install(old_install):
    """Installs Dnuos locally"""

    def finalize_options(self):
        import sys
        has_local = False
        for path in sys.path:
            if path.startswith('/usr/local'):
                has_local = True
                break
        if has_local:
            from distutils.sysconfig import get_config_vars
            prefix, exec_prefix = get_config_vars('prefix', 'exec_prefix')
            if not self.prefix and prefix == '/usr':
                self.prefix = '/usr/local'
            if not self.exec_prefix and exec_prefix == '/usr':
                self.exec_prefix = '/usr/local'
        old_install.finalize_options(self)


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
    cmdclass={'build_py': build_py, 'install': install, 'test': test},
    description='A tool for creating lists of music collections',
    download_url='http://bitheap.org/dnuos/files/dnuos-1.0.9.tar.gz',
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
    scripts=['scripts/dnuos'],
    url='http://bitheap.org/dnuos/',
    version='1.0.9',
    **extra_options
)
