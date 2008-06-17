=======
 Dnuos
=======

.. contents::

About
=====

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


Download
========

Releases can be found in https://github.com/aiiie/dnuos.


Installation/Usage
==================

Run ``dnuos --help`` for a full rundown of the available options.


Linux, Mac OS X, Unix
---------------------

Extract the archive and run ``setup.py`` to install it::

    tar zxvf dnuos-*.tar.gz
    cd dnuos-*
    sudo python setup.py install

This will install a console script named ``dnuos`` into ``/usr/local/bin``.
(On Mac OS X 10.4 and earlier, it may get installed into
``/Library/Frameworks/Python.framework/Versions/Current/bin``.)

Once installed, open up your favorite terminal emulator and run ``dnuos``. On
Mac OS X, *Terminal* might be a good choice (located in
``/Applications/Utilities/``).


Windows
-------

There's no installation. Just extract the zip file where you want to install
it. You can run the program in the command prompt with ``dnuos.exe``.

After extracting Dnuos, press the Windows key and R to bring up the *Run*
dialog. Type *cmd* and press enter to start the command prompt. Then type the
drive letter the ``.exe`` is on, and ``cd`` to the directory with the ``.exe``
file. From here, simply run ``dnuos.exe``.


Graphical Front-ends
--------------------

If terminals and command prompts aren't to your liking, you can try one of
the following graphical front-ends instead:

dnuOSX_
    A native front-end for Mac OS X.
Guidua_
    A graphical front-end for Windows.
QtOIDUA_
    A graphical front-end for Linux and Mac OS X. (Note: Versions 0.08 and
    older have a bug which prevents QtOIDUA from working with Dnuos 1.0)


.. _dnuOSX: http://www.facepwn.com/MacRequest/dnuOSX.html
.. _Guidua: http://oidua.suxbad.com/setup_guidua_0.16.exe
.. _QtOIDUA: http://www.spoonfedmonkey.com/software/qtoidua/


News
====

Version 1.0.8 (Jun. 16, 2008)
    Fixed crashes on Unix platforms with directory names that have
    characters that aren't valid for the file system's character encoding.

Version 1.0.7 (Jun. 3, 2008)
    Added consistency improvements from the Makefile to ``setup.py``. ``make``
    isn't always available, so ``setup.py`` is now the recommended way of
    installing Dnuos.

Version 1.0.6 (May 31, 2008)
    Moved cache location on Linux from ``~/.dnuos`` to ``~/.cache/dnuos``
    (``$XDG_CACHE_HOME/dnuos``).

    Made the Makefile more consistent across platforms. This is now the
    recommended way to install Dnuos.

    Fixed album and artist information not being populated for FLAC files.
    (Cached directories with FLAC files will be rescanned.)

    Fixed potential Unicode error crashes with file names that aren't
    properly encoded with the file system's character encoding.

Version 1.0.5 (May 5, 2008)
    Fixed potential Unicode error crashes due to UTF-8 cache format
    transition.

Version 1.0.4 (May 4, 2008)
    Greatly improved support for file and directory names with Unicode
    characters on Windows. Dnuos should now be able to scan folders and open
    audio files with Unicode characters in their paths, and Unicode
    characters can now be used in command line arguments.

    Improved cache format support between Python versions.

Version 1.0.3 (Apr. 27, 2008)
    Fixed a crash with malformed locale environment variables (e.g.
    ``LANG``, ``LC_ALL``, etc.)

    Fixed incorrect output when scanning root drive folders on Windows
    (e.g. ``C:\``).

Version 1.0.2 (Mar. 29, 2008)
    Fixed ``-V``/``--version`` not working in regular output.

Version 1.0.1 (Mar. 24, 2008)
    Improved printing of ID3 tags with null bytes.

    Fixed Python 2.3 compatibility.

    Fixed possible cache-related crash on certain Mac OS X environments.

Version 1.0 (Mar. 20, 2008)
    Added ``--delete-cache`` for deleting the cache directory and
    ``--cull-cache`` for removing non-existent directories from the cache.

    Updated French translation.

Version 1.0b7 (Mar. 10, 2008)
    Updated French translation with corrections.

    Fixed crash on displaying sizes in terabytes or higher.

    Fixed Unicode-related crashes. UTF-8 is now used unconditionally.

Version 1.0b6 (Feb. 24, 2008)
    Fixed cache creation not working on Windows.

Version 1.0b5 (Feb. 23, 2008)
    Added ``-L``/``--list-files`` for listing individual files in
    directories. Information about individual files isn't cached, however.

    Added ``-u``/``--unknown-types`` for listing directories with unsupported
    audio types.

    Fixed creation of the cache directory failing.

Version 1.0b4 (Feb. 22, 2008)
    Added support for locale-specific number formatting.

    Fixed Audiolist tag crashing on VBR MP3s.

    Fixed crashing on inaccessible directories (now ignored).

    Added support for gettext-based translation.

    Added a French translation.

    Fixed theoretically possible zero division error with ``-t``/``--time``.

    Fixed issues with the cache not caching correctly (and non-existent
    directories now get culled from the cache).

    Improved the cache implementation so it's loaded incrementally instead
    of all at once before a list is printed.

    Fixed ``-e`` exclude directory switch not working with relative paths.

    Fixed crash with ``-w``/``--wildcards``.

    Fixed ``-m``/``--merge`` not working properly on Windows.

    Improved unit test coverage and fixed Windows portability issues.

Version 1.0b3 (Dec. 25, 2007)
    Added support for saving the cache even when Dnuos is interrupted.

    Renamed ``-p``/``--parallel`` back to ``-m``/``--merge``, as it does
    just that.

    Fixed ``-i``/``--ignore-case`` not working.

    Marginal speed improvements in ``audiotype`` and ``id3`` code.

    Removed a substantial amount of unused code in the ``id3`` package.

    Fixed possible crash with new vendor output field in certain cases.

    Fixed parsing errors with Ogg Vorbis files and added vendor support.

    Reduced win32 package size.

Version 1.0b2 (Dec. 7, 2007)
    Updated and consolidated documentation.

    Fixed ``setup.py sdist`` not including all files.

    Fixed handling of MP3s with VBRI headers (e.g. made by Fraunhofer).

    Fixed serious issues with ID3 code that made it probably never work.

    Fixed an import of ``set()`` (should improve Python 2.3 compatibility).

    Switched from ``pickle`` to ``cPickle`` (when available) and switched to
    the most efficient pickle format (should speed things up quite a bit).

    Made cache directory finding more robust.

    Added support for saving the cache mid-list, so if you cancel making a
    list, it'll cache what it already listed.

    Added a friendly error message for output strings with invalid fields.

    Added a Makefile that runs ``setup.py``.

Version 1.0b1 (Dec. 2, 2007)
    Significant code overhaul.

    Added audio metadata caching.

    Added the ability to filter out directories with mixed files.

    Added proper ``distutils``/``setuptools`` support.

    Added AAC bitrate calculation support.

    Added ``V`` output flag that prints the encoder info (only MP3s for now).

    Cleaned up help message (uses ``optparse`` now).

    Removed ``-m``/``--merge`` switch.

    Dropped support for Python 2.2.

Version 0.94 (Jan. 16, 2006)
    Fixed endianness issues on big-endian machines.

Version 0.93 (Jan. 13, 2006)
    Fixed regression with MP3 header detection.

    Added experimental VBRI header support.

Version 0.92 (Jan. 13, 2006)
    The ``-l`` (LAME MP3s only) and ``-v`` (VBR MP3s only) switches now work
    in regular output.

    Added ``-b`` switch. Allows filtering of MP3s with bit rates lower than
    specified by ``-b``.

Version 0.91 (Jan. 12, 2006)
    Made finding of MP3 headers more robust. MP3s encoded at ``-V 9`` with
    LAME 3.97b1 no longer confuse Dnuos.

Version 0.9 (Jan. 11, 2006)
    Finally forked Oidua! This is now DNUOS!


Development
===========

The official development repository can be found at
https://github.com/aiiie/dnuos. Download using Git_::

    git clone https://github.com/aiiie/dnuos.git my-dnuos

Running the test suite requires the `test data`_ (in the same directory as
``setup.py``). Once you have it, you can run the tests with the following
command::

    python setup.py test

If you find any problems, please submit a ticket on the `Trac site`_. The
Trac site is for development, not support, so please don't submit help
requests there.

.. _Git: https://git-scm.com
.. _nose: http://somethingaboutorange.com/mrl/projects/nose/
.. _test data: https://github.com/aiiie/dnuos
.. _Trac site: https://github.com/aiiie/dnuos


Contact
=======

`Mattias Päivärinta <pejve at vasteras2 dot net>`_
    Senior programmer.
`aiiie <aiiie at aiiie dot co>`_
    Project maintainer.
