#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Script gathering information about directory trees of audio files
#
# This program is under GPL license. See COPYING file for details.
#
# Copyright 2003,2006
# Sylvester Johansson <sylvestor@telia.com>
# Mattias Päivärinta <pejve@vasteras2.net>
#
# Authors
# Sylvester Johansson <sylvestor@telia.com>
# Mattias Päivärinta <pejve@vasteras2.net>


r"""Usage:  dnuos.py [options] <basedir> ...

Options:
  -b, --bitrate MIN     Exclude MP3s with bitrate lower than MIN (in Kbps)
  -B, --bg COLOR        Set HTML background color
  -D, --date            Display datestamp header
      --debug           Output debug trace to stderr
  -e, --exclude DIR     Exclude dir from search
  -f, --file FILE       Write output to FILE (cannot be used with -O /
                        --output-db)
  -h, --help            Display this message
  -H, --html            HTML output
      --ignore-bad      Don't list files that cause Audiotype failure
  -i, --ignore-case     Case-insensitive directory sorting
  -I, --indent N        Set indent to N
  -l, --lame-only       Exclude MP3s with no LAME profile
  -L, --lame-old-preset Report "--alt-preset xxx" for "-V x" LAME MP3s
                        where applicable

  -m, --merge           Merge identical directories

                        Basedirs with identical names are merged. This Means
                        that all their subdirs are considered being subdirs of
                        a single directory, and therefore sorted and displayed
                        together. If there are duplicate names among the
                        subdirs then those are also merged.

  -o, --output STRING   Set output format to STRING

                        Anything enclosed by brackets is considered a field. A
                        field must have the following syntax:
                          [TAG]
                          [TAG,WIDTH]
                          [TAG,WIDTH,SUFFIX]
                          [TAG,,SUFFIX]

                        TAG is any of the following characters:
                          a     list of bitrates in Audiolist compatible format
                          A     artist name as found in ID3 tags
                          b     bitrate with suffix (i.e. 192k)
                          B     bitrate in bps
                          C     album name as found in ID3 tags
                          D     depth; distance from respective basedir
                          f     number of audio files (including spacers)
                          l     length in minutes and seconds
                          L     length in seconds
                          m     time of last change
                          M     time of last change in seconds since the epoch
                          n     directory name (indented)
                          N     directory name
                          p     profile
                          P     full path
                          q     quality
                          s     size with suffix (i.e. 65.4M)
                          S     size in bytes
                          t     file type
                          T     bitrate type:
                                  ~     mixed files
                                  C     constant bitrate
                                  L     lossless compression
                                  V     variable bitrate

                        WIDTH defines the exact width of the field. The output
                        is cropped to this width if needed. Negative values will
                        give left aligned output. Cropping is always done on the
                        right.

                        SUFFIX lets you specify a unit to be concatenated to
                        all non-empty data.

                        Other interpreted sequences are:
                          \[    [
                          \]    ]
                          \n    new line
                          \t    tab character

                        Unescaped brackets are forbidden unless they define a
                        field.

                        Note: If you have any whitespace in your output string
                        you must put it inside quotes or otherwise it will not
                        get parsed right.

  -O, --output-db FILE  Print list in output.db format to FILE
  -P, --prefer-tag N    If both ID3v1 and ID3v2 tags exist, prefer N (1 or 2)
  -q, --quiet           Omit progress indication
  -s, --strip           Strip output of field headers and empty directories
  -S, --stats           Display statistics results
  -t, --time            Display elapsed time footer
  -T, --text COLOR      Set HTML text color
  -v, --vbr-only        Exclude MP3s with constant bitrates
  -V, --version         Display version
  -w, --wildcards       Expand wildcards in basedirs
"""


__version__ = "0.93"

import itertools
import os
import string
import sys
import time

# fix for some dumb version of python 2.3
sys.path.append(os.path.abspath('.'))

import audiotype
import audiodir
import conf


class Data:
    def __init__(self):
        self.bad_files = []
        self.start = 0
        self.size = {
            "Total": 0.0,
            "FLAC": 0.0,
            "Ogg": 0.0,
            "MP3": 0.0,
            "MPC": 0.0,
            "AAC": 0.0}
        self.elapsed_time = 0.0


def to_human(value, radix=1024.0):
    i = 0
    while value >= radix:
        value /= radix
        i += 1
    suffix = " kMG"[i]
    if value > 100:
        return "%d%s" % (value, suffix)
    elif value < 10:
        return "%.2f%s" % (value, suffix)
    else:
        return "%.1f%s" % (value, suffix)


def eval_fields(fields, obj, suffixes=1):
    """project an object through a field list into a tuple of strings"""
    result = []
    for field in fields:
        try:
            data, width, suffix = str(obj.get(field[0])), field[1], field[2]
        except KeyError:
            msg = "Unknown field <%s> in format string" % field[0]
            print >> sys.stderr, msg
            sys.exit(1)
        if not data:
            suffix = " " * len(suffix)
        if suffixes:
            data += suffix
        if width != None:
            data = "%*.*s" % (width, abs(width), data)
        result.append(data)
    return tuple(result)


def main():
    if conf.conf.DispHelp:
        print >> sys.stderr, __doc__
        return 0

    if conf.conf.Folders:
        keys = conf.conf.Folders.keys()
        conf.conf.sort(keys)
        bases = [ conf.conf.Folders[k] for k in keys ]
        trees = [ walk(base) for base in bases ]
        dirs = itertools.chain(*trees)

        dirs = timer_wrapper(dirs)
        dirs = indicate_progress(dirs)
        if not conf.conf.OutputDb:
            dirs = collect_bad(dirs)
        dirs = filter_dirs(dirs)
        if not conf.conf.OutputDb:
            dirs = total_sizes(dirs)

        if conf.conf.OutputDb:
            outputdb(dirs)
        elif conf.conf.OutputFormat == "HTML":
            outputhtml(dirs)
        else:
            outputplain(dirs)

    elif conf.conf.DispVersion:
        print ""
        print "dnuos version:    ", __version__
        print "audiotype version:", audiotype.__version__


def headers(token):
    if token == "header" and not conf.conf.Stripped:  #top header
        fields = eval_fields(conf.conf.Fields, HeaderObject(), 0)
        line = conf.conf.OutputString % fields
        print line
        print "=" * len(line)
    elif token == "date":  #date
        print time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())


def debug(msg):
    """print debug message"""
    if conf.conf.Debug:
        print >> sys.stderr, "?? " + msg


class HeaderObject:
    def __init__(self):
        pass

    def get(self, id):
        dict = {
            "a": "Bitrate(s)",
            "A": "Artist",
            "b": "Bitrate",
            "B": "Bitrate",
            "c": "Channels",
            "C": "Album",
            "d": "Dir",
            "D": "Depth",
            "f": "Files",
            "l": "Length",
            "L": "Length",
            "m": "Modified",
            "n": "Album/Artist",
            "N": "Album/Artist",
            "p": "Profile",
            "P": "Path",
            "q": "Quality",
            "r": "Sample Rate",
            "s": "Size",
            "S": "Size",
            "t": "Type",
            "T": "BR Type"
            #"v": "Vendor",
            #"V": "Version",
            }
        return dict[id]


def indicate_progress(dirs, outs=sys.stderr):
    """Indicate progress.

    Yields an unchanged iteration of dirs with an added side effect.
    Total size in GLOBALS.size is updated to stderr every step
    throughout the iteration.
    """
    for adir in dirs:
        print >> outs, "%sb processed\r" % to_human(GLOBALS.size["Total"]),
        yield adir
    print >> outs, "\r               \r",


def collect_bad(dirs):
    """Collect bad files.

    Yields an unchanged iteration of dirs with an added side effect.
    After each directory is yielded its bad files are taken care of.
    Bad files are appended to GLOBALS.Badfiles or output to stderr
    depending on conf.conf.Debug.
    """
    for adir in dirs:
        yield adir

        if conf.conf.Debug:
            for badfile in adir.bad_streams():
                print >> sys.stderr, "Audiotype failed for:", badfile
        elif conf.conf.ListBad:
            GLOBALS.bad_files += adir.bad_streams()


def filter_dirs(dirs):
    """Filter directories according to configuration.

    Directories with no recognized files are always omitted.
    Directories can also be omitted as per -bvL settings.
    """
    for adir in dirs:
        if not adir.streams():
            continue
        if hasattr(adir, "type") and adir.type() == "MP3":
            if conf.conf.NoCBR == 1 and adir.brtype() in "C~":
                continue
            if conf.conf.NoNonProfile == 1 and adir.profile() == "":
                continue
            if adir.bitrate() < conf.conf.MP3MinBitRate:
                continue
            if conf.conf.OutputDb and \
               (adir.type() == "Mixed" or \
                adir.get('A') == None or \
                adir.get('C') == None):
                continue

        yield adir


def total_sizes(dirs):
    """Calculate audio file size totals.

    Yields an unchanged iteration of dirs with an added side effect.
    After each directory is yielded its filesize statistics are
    added to GLOBALS.size.
    """
    for adir in dirs:
        yield adir
        for mediatype in adir.types():
            GLOBALS.size[mediatype] += adir.size(mediatype)
        GLOBALS.size["Total"] += adir.size()


def timer_wrapper(dirs):
    """Time the iteration.

    Yields an unchanged iteration of dirs with an added side effect.
    Time in seconds elapsed over the iteration is stored in
    GLOBALS.elapsed_time.
    """
    GLOBALS.start = time.clock()
    for adir in dirs:
        yield adir
    GLOBALS.elapsed_time = time.clock() - GLOBALS.start


class EmptyDir:
    """
    Represent a group of merged empty directories.
    """
    def __init__(self, name, depth):
        self.name = name
        self.depth = depth

    def get(self, id):
        if id == "n":
            return ' ' * conf.conf.Indent * self.depth + self.name
        else:
            return ""


def outputplain(dirs):
    """Render directories to stdout.

    Directories are rendered according to the -o settings. Ancestral
    directories are rendered as empty unless they were previously
    rendered. Pre-order directory tree traversal is assumed.
    """
    if conf.conf.DispDate:
        headers("date")
    headers("header")

    oldpath = []
    for adir in dirs:
        # output empty ancestor directories
        path = adir.path.split(os.path.sep)[-adir.depth-1:]
        i = 0
        while i < len(path) - 1 and \
              i < len(oldpath) and \
              path[i] == oldpath[i]:
            i += 1
        while i < len(path) - 1:
            fields = eval_fields(conf.conf.Fields, EmptyDir(path[i], i))
            print conf.conf.OutputString % fields
            i += 1
        oldpath = path

        # output audiodir
        fields = eval_fields(conf.conf.Fields, adir)
        print conf.conf.OutputString % fields

    if GLOBALS.bad_files:
        print ""
        print "Audiotype failed on the following files:"
        print string.join(GLOBALS.bad_files, "\n")

    if conf.conf.DispTime:
        print ""
        print "Generation time:     %8.2f s" % GLOBALS.elapsed_time

    if conf.conf.DispResult:
        statistics = [
            ["Ogg", GLOBALS.size["Ogg"]],
            ["MP3", GLOBALS.size["MP3"]],
            ["MPC", GLOBALS.size["MPC"]],
            ["AAC", GLOBALS.size["AAC"]],
            ["FLAC", GLOBALS.size["FLAC"]]]
        line = "+-----------------------+-----------+"

        print ""
        print line
        print "| Format    Amount (Mb) | Ratio (%) |"
        print line
        for x in statistics:
            if x[1]:
                print "| %-8s %12.2f | %9.2f |" % (
                    x[0],
                    x[1] / (1024 * 1024),
                    x[1] * 100 / GLOBALS.size["Total"])
        print line
        total_megs = GLOBALS.size["Total"] / (1024 * 1024)
        print "| Total %10.2f Mb   |" % total_megs
        print "| Speed %10.2f Mb/s |" % (total_megs / GLOBALS.elapsed_time)
        print line[:25]

    if conf.conf.DispVersion:
        print ""
        print "dnuos version:    ", __version__
        print "audiotype version:", audiotype.__version__


def outputhtml(dirs):
    """Render directories as HTML to stdout.

    Directories are rendered like in plain text, but with HTML header
    and footer.
    """
    print """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<title>Music List</title>
<!-- Generated by dnuos %s -->
<!-- http://dackz.net/projects/dnuos -->
<style type="text/css"><!--
body { color: %s; background: %s; }
-->
</style>
</head>
<body>
<pre>""" % (__version__, conf.conf.TextColor, conf.conf.BGColor)

    outputplain(dirs)

    print"</pre>"
    print"</body></html>"


def outputdb(dirs):
    for adir in dirs:
        print "%d:'%s',%d:'%s',%d:'%s',%d:'%s',%d,%.d,%d" % (
            len(str(adir.get('A'))),
            str(adir.get('A')),
            len(str(adir.get('C'))),
            str(adir.get('C')),
            len(str(adir.get('t'))),
            str(adir.get('t')),
            len(str(adir.get('p'))),
            str(adir.get('p')),
            adir.get('f'),
            adir.get('B') / 1000,
            adir.get('L')
        )


def subdirectories(dirs):
    dirdict = {}
    for adir in dirs:
        for path in adir.subdirs():
            key = os.path.basename(path)
            if dirdict.has_key(key):
                dirdict[key].append(path)
            else:
                dirdict[key] = [ path ]
    return dirdict


def walk(pathlist, depth=0):
    """Traverse one or more merged directory trees in parallell in pre order.

    The subdirectories of all pathlist directories are considered
    together. They are traversed in lexicographical order by basename.
    If subdirectories of two or more pathlist directories share the same
    basename, those subdirectories are traversed together.
    """
    # create Dir objects for all paths
    dirs = map(lambda x: audiodir.Dir(x, depth), pathlist)

    # enumerate dirs
    for adir in dirs:
        yield adir

    # create a common dictionary over the subdirectories of all Dirs
    subdir_dict = subdirectories(dirs)

    # sort keys and traverse the dictionary
    keys = subdir_dict.keys()
    conf.conf.sort(keys)
    for key in keys:
        # weed out base and excluded directories
        cond = lambda path: path not in conf.conf.ExcludePaths
        dirs = filter(cond, subdir_dict[key])

        # recurse
        for adir in walk(dirs, depth + 1):
            yield adir


if __name__ == "__main__":
    GLOBALS = Data()
    conf.init()
    try:
        main()
    except KeyboardInterrupt:
        print >> sys.stderr, "Aborted by user"
        sys.exit(1)
