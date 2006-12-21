#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# This program is under GPL license. See COPYING file for details.
#
# Copyright 2003,2006
# Sylvester Johansson <sylvestor@telia.com>
# Mattias P�iv�rinta <pejve@vasteras2.net>
#
# Authors
# Sylvester Johansson <sylvestor@telia.com>
# Mattias P�iv�rinta <pejve@vasteras2.net>

"""
Script gathering information about directory trees of audio files
"""

__version__ = "0.93"

from heapq import heappop, heappush
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
    """Convert a value to a string using SI suffixes"""
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
    if conf.conf.Folders:
        trees = [ walk(basedir) for basedir in conf.conf.Folders ]
        if conf.conf.options.merge:
            dirs = merge(*trees)
        else:
            dirs = itertools.chain(*trees)

        dirs = timer_wrapper(dirs)
        if not conf.conf.options.quiet:
            dirs = indicate_progress(dirs)
        if not conf.conf.options.output_format == 'db':
            dirs = collect_bad(dirs)
        dirs = filter_dirs(dirs)
        if not conf.conf.options.output_format == 'db':
            dirs = total_sizes(dirs)

        if conf.conf.options.output_format == 'db':
            outputdb(dirs)
        elif conf.conf.options.output_format == "HTML":
            outputhtml(dirs)
        else:
            outputplain(dirs)

    elif conf.conf.options.disp_version:
        print ""
        print "dnuos version:    ", __version__
        print "audiotype version:", audiotype.__version__


def debug(msg):
    """print debug message"""
    if conf.conf.options.debug:
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
    depending on conf.conf.options.debug.
    """
    for adir in dirs:
        yield adir

        if conf.conf.options.debug:
            for badfile in adir.bad_streams():
                print >> sys.stderr, "Audiotype failed for:", badfile
        elif conf.conf.options.list_bad:
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
            if conf.conf.options.no_cbr == 1 and adir.brtype() in "C~":
                continue
            if conf.conf.options.no_non_profile == 1 and adir.profile() == "":
                continue
            if adir.bitrate() < conf.conf.options.mp3_min_bit_rate:
                continue
        if conf.conf.options.output_format == 'db' and \
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
            return conf.conf.indent(self.name, self.depth)
        else:
            return ""


def outputplain(dirs):
    """Render directories to stdout.

    Directories are rendered according to the -o settings. Ancestral
    directories are rendered as empty unless they were previously
    rendered. Pre-order directory tree traversal is assumed.
    """
    # output date
    if conf.conf.options.disp_date:
        print time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())

    # output column headers
    fields = eval_fields(conf.conf.Fields, HeaderObject(), 0)
    line = conf.conf.OutputString % fields
    print line
    print "=" * len(line)

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

    if conf.conf.options.disp_time:
        print ""
        print "Generation time:     %8.2f s" % GLOBALS.elapsed_time

    if conf.conf.options.disp_result:
        line = "+-----------------------+-----------+"

        print ""
        print line
        print "| Format    Amount (Mb) | Ratio (%) |"
        print line
        for mediatype in ["Ogg", "MP3", "MPC", "AAC", "FLAC"]:
            if GLOBALS.size[mediatype]:
                print "| %-8s %12.2f | %9.2f |" % (
                    mediatype,
                    GLOBALS.size[mediatype] / (1024 * 1024),
                    GLOBALS.size[mediatype] * 100 / GLOBALS.size["Total"])
        print line
        total_megs = GLOBALS.size["Total"] / (1024 * 1024)
        print "| Total %10.2f Mb   |" % total_megs
        print "| Speed %10.2f Mb/s |" % (total_megs / GLOBALS.elapsed_time)
        print line[:25]

    if conf.conf.options.disp_version:
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
<pre>""" % (__version__, conf.conf.options.text_color, conf.conf.options.bg_color)

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


class Lookahead:
    """Wrapper class for adding one element of lookahead to iterators"""
    def __init__(self, iterable):
        self.iterable = iterable
        self.lookahead = None
        self.empty = False
        self.next()

    def next(self):
        result = self.lookahead
        try:
            self.lookahead = self.iterable.next()
        except StopIteration:
            self.lookahead = None
            self.empty = True
        return result

    def __le__(self, other): return self.lookahead <= other.lookahead
    def __eq__(self, other): return self.lookahead == other.lookahead


def merge(*iterators):
    """Merge n ordered iterators into one ordered iterator"""
    heap = []
    for index in range(0, len(iterators)):
        iterator = Lookahead(iterators[index])
        if not iterator.empty:
            heappush(heap, (iterator, index))

    while heap:
        iterator, index = heappop(heap)
        yield iterator.next()
        if not iterator.empty:
            heappush(heap, (iterator, index))


def subdirs(path):
    """Create a sorted iterable of subdirs"""
    subdirs = [ (conf.conf.cmp_munge(os.path.basename(sub)),
                 os.path.join(path, sub))
                for sub in os.listdir(path) ]
    subdirs = [ (key, sub) for key, sub in subdirs
                if audiodir.dir_test(sub) and
                   sub not in conf.conf.options.exclude_paths ]
    subdirs.sort()
    for key, sub in subdirs:
        yield sub


def walk(path, depth=0):
    """Traverse a directory tree in pre-order"""
    yield audiodir.Dir(path, depth)

    # recurse each subdir
    for subpath in subdirs(path):
        for descendant in walk(subpath, depth+1):
            yield descendant


if __name__ == "__main__":
    GLOBALS = Data()
    conf.init()
    try:
        main()
    except KeyboardInterrupt:
        print >> sys.stderr, "Aborted by user"
        sys.exit(1)
