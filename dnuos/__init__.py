#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# This program is under GPL license. See COPYING file for details.
#
# Copyright 2003,2006,2007
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
import warnings

# fix for some dumb version of python 2.3
sys.path.append(os.path.abspath('.'))

import appdata
import audiotype
import audiodir
from cache import PersistentDict
from conf import Settings
from misc import dir_depth
from misc import equal_elements
from misc import formatwarning
from misc import make_included_pred
from misc import merge
from misc import sort
from misc import to_human
import output


class Data(object):
    def __init__(self):
        self.bad_files = []
        self.size = {
            "Total": 0.0,
            "FLAC": 0.0,
            "Ogg": 0.0,
            "MP3": 0.0,
            "MPC": 0.0,
            "AAC": 0.0,
        }
        self.times = {
            'start': 0,
            'elapsed_time': 0.0,
        }
        self.version = {
            'dnuos': __version__,
            'audiotype': audiotype.__version__,
        }

def make_listing(options, data):
    # Make an iterator over all subdirectories of the base directories,
    # including the base directories themselves. The directory trees are
    # sorted either separately or together according to the merge setting.
    trees = [ walk(basedir, options.sort_key, options.exclude_paths)
              for basedir in options.basedirs ]
    if options.merge:
        path_pairs = merge(*trees)
    else:
        path_pairs = chain(*trees)

    # Make Dirs from paths
    if options.use_cache:
        dirs = to_adir(path_pairs, audiodir.CachedDir)
    else:
        dirs = to_adir(path_pairs, audiodir.Dir)

    # Add layers of functionality
    dirs = timer_wrapper(dirs, data.times)
    if options.show_progress:
        dirs = indicate_progress(dirs, data.size)
    if options.debug:
        dirs = print_bad(dirs)
    elif options.list_bad:
        dirs = collect_bad(dirs, data.bad_files)
    dirs = ifilter(non_empty, dirs)
    if options.no_cbr:
        dirs = ifilter(no_cbr_mp3, dirs)
    if options.no_non_profile:
        dirs = ifilter(profile_only_mp3, dirs)
    if options.mp3_min_bit_rate != 0:
        dirs = ifilter(enough_bitrate_mp3(options.mp3_min_bit_rate), dirs)
    if options.output_module == output.db:
        dirs = ifilter(output_db_predicate, dirs)
    if not options.output_module == output.db:
        dirs = total_sizes(dirs, data.size)
    if not options.stripped and \
       options.output_module in [output.plaintext, output.html]:
        dirs = add_empty(dirs)

    # Setup renderer
    renderer = options.output_module.Renderer()
    renderer.format_string = options.format_string
    renderer.columns = options.fields
    return renderer.render(dirs, options, data)


def main():
    try:
        warnings.formatwarning = formatwarning

        data = Data()
        options = Settings().parse_args(sys.argv[1:])

        if options.use_cache:
            is_path_included = make_included_pred(options.basedirs,
                                                  options.exclude_paths)
            is_entry_excluded = lambda (path,), value: \
                                       not is_path_included(path)
            cache = PersistentDict[audiodir.DIR_PERSISTENCE_FILE]
            cache.load(keep_pred=is_entry_excluded)

        if options.basedirs:
            result = make_listing(options, data)
        elif options.disp_version:
            result = output.plaintext.render_version(data.version)
        else:
            raise ValueError("No folders to process.\nType 'dnuos.py -h' for help.")

        # Output
        outfile = options.outfile and open(options.outfile, 'w') or sys.stdout
        for chunk in result:
            print >> outfile, chunk

        if options.use_cache:
            appdata.create_user_data_dir()
            PersistentDict.writeout()

    except ValueError, err:
        print >> sys.stderr, err
        return 2

    except KeyboardInterrupt:
        print >> sys.stderr, "Aborted by user"
        return 1

    except IOError, (errno, errstr):
        print >> sys.stderr, "I/O Error(%s): %s" % (errno, errstr)
        print >> sys.stderr, "Cannot open '%s' for writing" % filename
        return 1


def indicate_progress(dirs, sizes, outs=sys.stderr):
    """Indicate progress.

    Yields an unchanged iteration of dirs with an added side effect.
    Total size in sizes is updated to stderr every step
    throughout the iteration.
    """
    for adir in dirs:
        print >> outs, "%sB processed\r" % to_human(sizes["Total"]),
        yield adir
    print >> outs, "\r               \r",


def print_bad(dirs):
    """Print bad files.

    Yields an unchanged iteration of dirs with an added side effect.
    After each directory is yielded its bad files are output to
    stderr.
    """
    for adir in dirs:
        yield adir

        for badfile in adir.bad_files:
            print >> sys.stderr, "Audiotype failed for:", badfile


def collect_bad(dirs, bad_files):
    """Collect bad files.

    Yields an unchanged iteration of dirs with an added side effect.
    After each directory is yielded its bad files are appended to
    bad_files.
    """
    for adir in dirs:
        yield adir

        bad_files.extend(adir.bad_files)


def non_empty(adir):
    """Empty directory predicate

    Directories are considered empty if they contain no recognized audio files.
    """
    return adir.num_files > len(adir.bad_files)
 

def no_cbr_mp3(adir):
    """No CBR MP3 files predicate"""
    # This implentation does not consider CBR MP3s in Mixed directories
    return adir.mediatype != "MP3" or adir.brtype not in "C~"


def profile_only_mp3(adir):
    """No non-profile MP3 predicate"""
    # This implentation does not consider non-profile MP3s in Mixed directories
    return adir.mediatype != "MP3" or adir.profile != ""


def enough_bitrate_mp3(mp3_min_bit_rate):
    """Create low-bitrate MP3 predicate"""
    # This implentation does not consider low-bitrate MP3s in Mixed directories
    return lambda adir: (adir.mediatype != "MP3" or
                         adir.bitrate >= mp3_min_bit_rate)


def output_db_predicate(adir):
    return adir.mediatype != "Mixed" and \
           adir.artist != None and \
           adir.album != None


def total_sizes(dirs, sizes):
    """Calculate audio file size totals.

    Yields an unchanged iteration of dirs with an added side effect.
    After each directory is yielded its filesize statistics are
    added to sizes.
    """
    for adir in dirs:
        yield adir
        for mediatype, size in adir.sizes.items():
            sizes[mediatype] += size
        sizes["Total"] += adir.size


def timer_wrapper(dirs, times):
    """Time the iteration.

    Yields an unchanged iteration of dirs with an added side effect.
    Time in seconds elapsed over the iteration is stored in times.
    """
    times['start'] = time.clock()
    for adir in dirs:
        yield adir
    times['elapsed_time'] = time.clock() - times['start']


class EmptyDir(object):
    """Represent a group of merged empty directories."""

    __slots__ = ['_depth', 'name']

    def __init__(self, name, depth):
        self.name = name
        self._depth = depth

    def __getattr__(self, attr):
        return None


def add_empty(dirs):
    """Insert empty ancestral directories

    Pre-order directory tree traversal is assumed.
    """
    oldpath = []
    for adir in dirs:
        path = adir._relpath.split(os.path.sep)
        start = equal_elements(path, oldpath)
        for depth in range(start, len(path) - 1):
            yield EmptyDir(path[depth], depth)
        oldpath = path

        yield adir


def walk(basedir, sort_key=lambda x: x, excluded=[]):
    """Traverse a directory tree in pre-order

    Directories are sorted according to the --ignore-case setting and branches
    specified by --exclude are ignored.
    """

    root = os.path.dirname(basedir)

    for dirname, subdirs, _ in os.walk(basedir):
        # Give os.walk directions for further traversal
        subdirs = sort([ sub for sub in subdirs if sub not in excluded ],
                       sort_key)

        yield dirname[len(root):], root


def to_adir(path_pairs, constructor):
    """
    Converts a sequence of path pairs into a sequence of Dirs

    A path pair is a tuple (relpath, root). The Dir is validated and root is
    assigned to it.
    """
    for relpath, root in path_pairs:
        adir = constructor(root + relpath)
        adir.validate()
        audiodir.set_root(adir, root)
        yield adir
