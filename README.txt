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

Run ``setup.py`` with the version of Python you wish to install Dnuos with::

    sudo python2.5 setup.py install

This will install Dnuos into your ``site-packages`` folder, and will add a
console script named ``dnuos`` (usually in ``/usr/bin/`` or
``/usr/local/bin/``).

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

Guidua_
    A graphical front-end for Windows.
QtOIDUA_
    A graphical front-end for Linux and Mac OS X.
    

.. _Guidua: http://oidua.suxbad.com/setup_guidua_0.16.exe
.. _QtOIDUA: http://www.spoonfedmonkey.com/software/qtoidua/


News
====

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
https://github.com/aiiie/dnuosdarcs/. Download the directory recursively, or use
Darcs_::

    darcs get https://github.com/aiiie/dnuosdarcs/ my-dnuos-repo

Running the test suite requires nose_, and the `test data`_. Once you have
both, you can run the tests with the following command::

    ./setup.py test

If you find any problems, please submit a ticket on the `Trac site`_. The
Trac site is for development, not support, so please don't submit help
requests there.

.. _Darcs: http://darcs.net/
.. _nose: http://somethingaboutorange.com/mrl/projects/nose/
.. _test data: https://github.com/aiiie/dnuos
.. _Trac site: https://github.com/aiiie/dnuos


Contact
=======

`Mattias Päivärinta <pejve at vasteras2 dot net>`_
    Senior programmer.
`aiiie <aiiie at aiiie dot co>`_
    Project maintainer.
