Dnuos: Make a list!
===================

Dnuos is a console program that creates lists of music collections, based on
directory structure.

For example, a list might look like this:

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
profile detection is also supported, including [LAME quality preset][]
information.

Audio file information is saved to disk after a list is made for the first
time, making subsequent lists much faster to generate. Only audio files and
directories that have been changed since the last list was made are
analyzed.

Dnuos is based on code from [Oidua][]. Oidua makes similar lists, but is much
older, has fewer features, and is no longer maintained.

[LAME quality preset]: http://wiki.hydrogenaudio.org/index.php?title=Lame#Recommended_encoder_settings
[Oidua]: http://oidua.suxbad.com/


Download
--------

Releases can be found in <https://github.com/aiiie/dnuos>.


Installation/Usage
------------------

Run `dnuos --help` for a full rundown of the available options.

### Linux, Mac OS X, Unix

Extract the archive and run `setup.py` to install it:

    tar zxvf dnuos-1.0.10.tar.gz
    cd dnuos-1.0.10
    sudo python setup.py install

This will install a console script named `dnuos` into `/usr/local/bin`.
(On Mac OS X 10.4 and earlier, it may get installed into
`/Library/Frameworks/Python.framework/Versions/Current/bin`.)

Once installed, open up your favorite terminal emulator and run `dnuos`. On
Mac OS X, *Terminal* might be a good choice (located in
`/Applications/Utilities/`).


### Windows

There's no installation. Just extract the zip file where you want to install
it. You can run the program in the command prompt with `dnuos.exe`.

After extracting Dnuos, press the Windows key and R to bring up the *Run*
dialog. Type *cmd* and press enter to start the command prompt. Then type the
drive letter the `.exe` is on, and `cd` to the directory with the `.exe`
file. From here, simply run `dnuos.exe`.


### Graphical Front-ends

If terminals and command prompts aren't to your liking, you can try one of
the following graphical front-ends instead:

* [dnuOSX][] - A native front-end for Mac OS X.
* [Guidua][] - A graphical front-end for Windows.
* [QtOIDUA][] - A graphical front-end for Linux and Mac OS X. (Note: Versions
  0.08 and older have a bug which prevents QtOIDUA from working with
  Dnuos 1.0.)

[dnuOSX]: http://www.facepwn.com/MacRequest/dnuOSX.html
[Guidua]: http://oidua.suxbad.com/setup_guidua_0.16.exe
[QtOIDUA]: http://www.spoonfedmonkey.com/software/qtoidua/


News
----

### Version 1.0.10 (Feb. 13, 2009)

* Fixed installation not working when a previous egg-based installation is
  present.
* Fixed individual files not being sorted in output.
* Fixed unfriendly traceback being presented for non-existent files and
  directories.
* Added natural sorting (i.e. `9.mp3` comes before `10.mp3`).
* Added support for specifying individual files as arguments.
* Added default format string resizing based on the terminal width. The name
  column will be resized so the output better fits the width of the terminal.
  *(Unix only)*
* Added SQLite-based caching, available with Python 2.5. When used, loading
  the cache is much faster, and culling the cache reduces its total size.
* More Python 2.6 compatibility improvements.
* French translation corrections (contributed by Jean-Denis Vauguet).

### Version 1.0.9 (Sep. 20, 2008)

* Fixed a crash when using HTML output.
* Fixed a crash with FLAC/Ogg Vorbis tags containing equal signs.
* Fixed `--delete-cache` not always deleting the cache directory.
* Fixed directories with both LAME and non-LAME MP3s being listed with only
  the LAME preset quality, instead of being listed as mixed.
* Added shorthand switch `-C` for `--disable-cache`.
* Added the `[Y]` year output tag.
* Added the `[D]` depth output tag back.
* Improved Python 2.6 compatibility.
* Added support for using the preferred encoding when outputting to the
  terminal. (Characters that can't be encoded are replaced with question
  marks.)
* Updated French translation with corrections.
* Fixed French translation not being installed when using `easy_install`.

### Version 1.0.8 (Jun. 16, 2008)

* Fixed crashes on Unix platforms with directory names that have
  characters that aren't valid for the file system's character encoding.

### Version 1.0.7 (Jun. 3, 2008)

* Added consistency improvements from the Makefile to `setup.py`. `make`
  isn't always available, so `setup.py` is now the recommended way of
  installing Dnuos.

### Version 1.0.6 (May 31, 2008)

* Moved cache location on Linux from `~/.dnuos` to `~/.cache/dnuos`
  (`$XDG_CACHE_HOME/dnuos`).
* Made the Makefile more consistent across platforms. This is now the
  recommended way to install Dnuos.
* Fixed album and artist information not being populated for FLAC files.
  (Cached directories with FLAC files will be rescanned.)
* Fixed potential Unicode error crashes with file names that aren't
  properly encoded with the file system's character encoding.

### Version 1.0.5 (May 5, 2008)

* Fixed potential Unicode error crashes due to UTF-8 cache format
  transition.

### Version 1.0.4 (May 4, 2008)

* Greatly improved support for file and directory names with Unicode
  characters on Windows. Dnuos should now be able to scan folders and open
  audio files with Unicode characters in their paths, and Unicode
  characters can now be used in command line arguments.
* Improved cache format support between Python versions.

### Version 1.0.3 (Apr. 27, 2008)

* Fixed a crash with malformed locale environment variables (e.g.
  `LANG`, `LC_ALL`, etc.)
* Fixed incorrect output when scanning root drive folders on Windows
  (e.g. `C:\`).

### Version 1.0.2 (Mar. 29, 2008)

* Fixed `-V`/`--version` not working in regular output.

### Version 1.0.1 (Mar. 24, 2008)

* Improved printing of ID3 tags with null bytes.
* Fixed Python 2.3 compatibility.
* Fixed possible cache-related crash on certain Mac OS X environments.

### Version 1.0 (Mar. 20, 2008)

* Added audio metadata caching.
* Added French translation and support for localized number formatting.
* Added `-L`/`--list-files` for listing individual files in directories.
  Information about individual files isn't cached, however.
* Added `-u`/`--unknown-types` for listing directories with unsupported audio
  types.
* Implemented AAC bit rate calculation.
* Added `[V]` output flag that prints encoder information.
* Fixed handling of MP3s with VBRI headers (e.g. made by Fraunhofer).
* Cleaned up help messages.
* Dropped support for Python 2.2.


Development
-----------

The official development repository can be found at
<https://github.com/aiiie/dnuos>. Download using [Git][]:

    git clone https://github.com/aiiie/dnuos.git

Running the test suite requires the [test data][] (in the same directory as
`setup.py`). Once you have it, you can run the tests with the following
command:

    python setup.py test

If you find any problems, please submit a ticket on the [Trac site][]. The
Trac site is for development, not support, so please don't submit help
requests there.

[Git]: https://git-scm.com
[test data]: https://github.com/aiiie/dnuos
[Trac site]: https://github.com/aiiie/dnuos


Contact
-------

* [aiiie](mailto:aiiie at aiiie dot co) - Project maintainer

### Past Contributors

* [Mattias Päivärinta](mailto:pejve at vasteras2 dot net)
* frunksock
