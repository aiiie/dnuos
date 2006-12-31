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

from itertools import chain
from itertools import ifilter
import os
import sys
import time

# fix for some dumb version of python 2.3
sys.path.append(os.path.abspath('.'))

import audiotype
import audiodir
from conf import conf
from misc import die
from misc import equal_elements
from misc import merge
from misc import subdirs
import outputplain


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
        self.version = {
            'dnuos': __version__,
            'audiotype': audiotype.__version__,
        }


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
        # Enumerate directories
        trees = [ walk(basedir) for basedir in conf.Folders ]
        if conf.options.merge:
            dirs = merge(*trees)
        else:
            dirs = chain(*trees)

        # Add layers of functionality
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
        if not conf.options.stripped and \
           conf.options.output_format in ['plain', 'html']:
            dirs = add_empty(dirs)

        # Configure renderer
        output = conf.renderer.render(dirs, conf.options, GLOBALS)

    elif conf.options.disp_version:
        output = outputplain.render_version(GLOBALS.version)

    else:
        die("No folders to process.\nType 'dnuos.py -h' for help.", 2)

    # Output
    for chunk in output:
        print >> conf.OutStream, chunk


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
    return adir.type() != "MP3" or \
           adir.bitrate() >= conf.options.mp3_min_bit_rate


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

    def get(self, tag):
        if tag == "n":
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
        start = equal_elements(path, oldpath)
        for depth in range(start, len(path) - 1):
            yield EmptyDir(path[depth], depth)
        oldpath = path

        yield adir


def walk(path, depth=0):
    """Traverse a directory tree in pre-order"""
    yield audiodir.Dir(path, depth)

    # recurse each subdir
    for subpath in subdirs(path, conf.cmp_munge):
        if subpath in conf.options.exclude_paths:
            continue
        for descendant in walk(subpath, depth+1):
            yield descendant


if __name__ == "__main__":
    GLOBALS = Data()
    conf.parse_args()
    try:
        main()
    except KeyboardInterrupt:
        die("Aborted by user", 1)
