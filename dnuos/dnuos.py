#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
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

"""
Script gathering information about directory trees of audio files
"""

__version__ = "0.93"

from heapq import heappop, heappush
import itertools
from itertools import ifilter
import os
import string
import sys
import time

# fix for some dumb version of python 2.3
sys.path.append(os.path.abspath('.'))

import audiotype
import audiodir
from conf import conf
from misc import die


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


def main():
    if conf.Folders:
        trees = [ walk(basedir) for basedir in conf.Folders ]
        if conf.options.merge:
            dirs = merge(*trees)
        else:
            dirs = itertools.chain(*trees)

        dirs = timer_wrapper(dirs)
        if not conf.options.quiet:
            dirs = indicate_progress(dirs)
        if not conf.options.output_format == 'db':
            dirs = collect_bad(dirs)
        dirs = ifilter(non_empty, dirs)
        if conf.options.no_cbr:
            dirs = ifilter(no_cbr_mp3, dirs)
        if conf.options.no_non_profile:
            dirs = ifilter(profile_only_mp3, dirs)
        if conf.options.output_format == 'db':
            dirs = ifilter(output_db_predicate, dirs)
        if not conf.options.output_format == 'db':
            dirs = total_sizes(dirs)
        if not conf.options.output_format =='db' and \
           not conf.options.stripped:
            dirs = add_empty(dirs)

        if conf.options.output_format == 'db':
            output = outputdb(dirs)
        elif conf.options.output_format == "HTML":
            output = outputhtml(dirs)
        else:
            output = outputplain(dirs)

        for chunk in output:
            print >> conf.OutStream, chunk


    elif conf.options.disp_version:
        print ""
        print "dnuos version:    ", __version__
        print "audiotype version:", audiotype.__version__

    else:
        die("No folders to process.\nType 'dnuos.py -h' for help.", 2)


def debug(msg):
    """print debug message"""
    if conf.options.debug:
        print >> sys.stderr, "?? " + msg


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
    depending on conf.options.debug.
    """
    for adir in dirs:
        yield adir

        if conf.options.debug:
            for badfile in adir.bad_streams():
                print >> sys.stderr, "Audiotype failed for:", badfile
        elif conf.options.list_bad:
            GLOBALS.bad_files += adir.bad_streams()


def non_empty(adir):
    """Empty directory predicate

    Directories are considered empty if they contain no recognized audio files.
    """
    return len(adir.streams()) > 0
 

def no_cbr_mp3(adir):
    """No CBR MP3 files predicate"""
    # This implentation does not consider CBR MP3s in Mixed directories
    return adir.type() != "MP3" or adir.brtype() not in "C~"


def profile_only_mp3(adir):
    """No non-profile MP3 predicate"""
    # This implentation does not consider non-profile MP3s in Mixed directories
    return adir.type() != "MP3" or adir.profile() != ""


def enough_bitrate_mp3(adir):
    """No low-bitrate MP3 predicate"""
    # This implentation does not consider low-bitrate MP3s in Mixed directories
    return adir.type() != "MP3" or adir.bitrate() >= conf.options.mp3_min_bit_rate


def output_db_predicate(adir):
    return adir.type() != "Mixed" and \
           adir.get('A') != None and \
           adir.get('C') != None


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
            return conf.indent(self.name, self.depth)
        else:
            return ""


def add_empty(dirs):
    """Insert empty ancestral directories

    Pre-order directory tree traversal is assumed.
    """
    oldpath = []
    for adir in dirs:
        path = adir.path.split(os.path.sep)[-adir.depth-1:]
        i = 0
        while i < len(path) - 1 and \
              i < len(oldpath) and \
              path[i] == oldpath[i]:
            i += 1
        while i < len(path) - 1:
            yield EmptyDir(path[i], i)
            i += 1
        oldpath = path

        yield adir


def outputplain(dirs):
    """Render directories to stdout.

    Directories are rendered according to the -o settings.
    """
    # output date
    if conf.options.disp_date:
        yield time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())

    # output column headers
    if not conf.options.stripped:
        fields = map(lambda f: f.header(), conf.Fields)
        line = conf.OutputString % tuple(fields)
        yield line
        yield "=" * len(line)

    for adir in dirs:
        fields = map(lambda f: f.get(adir), conf.Fields)
        yield conf.OutputString % tuple(fields)

    if GLOBALS.bad_files:
        yield ""
        yield "Audiotype failed on the following files:"
        yield string.join(GLOBALS.bad_files, "\n")

    if conf.options.disp_time:
        yield ""
        yield "Generation time:     %8.2f s" % GLOBALS.elapsed_time

    if conf.options.disp_result:
        line = "+-----------------------+-----------+"

        yield ""
        yield line
        yield "| Format    Amount (Mb) | Ratio (%) |"
        yield line
        for mediatype in ["Ogg", "MP3", "MPC", "AAC", "FLAC"]:
            if GLOBALS.size[mediatype]:
                yield "| %-8s %12.2f | %9.2f |" % (
                    mediatype,
                    GLOBALS.size[mediatype] / (1024 * 1024),
                    GLOBALS.size[mediatype] * 100 / GLOBALS.size["Total"])
        yield line
        total_megs = GLOBALS.size["Total"] / (1024 * 1024)
        yield "| Total %10.2f Mb   |" % total_megs
        yield "| Speed %10.2f Mb/s |" % (total_megs / GLOBALS.elapsed_time)
        yield line[:25]

    if conf.options.disp_version:
        yield ""
        yield "dnuos version:    ", __version__
        yield "audiotype version:", audiotype.__version__


def outputhtml(dirs):
    """Render directories as HTML to stdout.

    Directories are rendered like in plain text, but with HTML header
    and footer.
    """
    yield """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<title>Music List</title>
<!-- Generated by dnuos %s -->
<!-- http://aiiie.net/projects/dnuos -->
<style type="text/css"><!--
body { color: %s; background: %s; }
-->
</style>
</head>
<body>
<pre>""" % (__version__, conf.options.text_color, conf.options.bg_color)

    for chunk in outputplain(dirs):
        yield chunk

    yield "</pre>"
    yield "</body></html>"


def outputdb(dirs):
    for adir in dirs:
        chunk = "%d:'%s',%d:'%s',%d:'%s',%d:'%s',%d,%.d,%d" % (
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
        yield chunk


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
    subdirs = [ (conf.cmp_munge(os.path.basename(sub)),
                 os.path.join(path, sub))
                for sub in os.listdir(path) ]
    subdirs = [ (key, sub) for key, sub in subdirs
                if audiodir.dir_test(sub) and
                   sub not in conf.options.exclude_paths ]
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
    conf.parse_args()
    try:
        main()
    except KeyboardInterrupt:
        die("Aborted by user", 1)
