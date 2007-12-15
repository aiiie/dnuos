"""Script for gathering information about directories of audio files"""

__version__ = '1.0b2'

import os
import sys
import time
import warnings
from itertools import chain
from itertools import ifilter

import dnuos.output
from dnuos import appdata, audiodir
from dnuos.cache import PersistentDict, memoized
from dnuos.conf import Settings
from dnuos.misc import dir_depth, equal_elements, formatwarning
from dnuos.misc import make_included_pred, merge, to_human
from dnuos.output.abstract_renderer import Column

class Data(object):
    """Holds data for cache"""

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
        self.version = __version__


def make_raw_listing(basedirs, exclude_paths, sort_key, use_merge,
                     adir_class):
    """Make an iterator over all subdirectories of the base directories,
    including the base directories themselves. The directory trees are
    sorted either separately or together according to the merge setting.
    """

    trees = [walk2(basedir, sort_key, exclude_paths)
             for basedir in basedirs]

    if use_merge:
        tree = merge(*trees)
    else:
        tree = chain(*trees)

    return to_adir(tree, adir_class)


def prepare_listing(dir_pairs, options, data):
    """Add layers of functionality"""

    dir_pairs = timer_wrapper(dir_pairs, data.times)
    if options.show_progress:
        dir_pairs = indicate_progress(dir_pairs, data.size)
    if options.debug:
        dir_pairs = print_bad(dir_pairs)
    elif options.list_bad:
        dir_pairs = collect_bad(dir_pairs, data.bad_files)
    dir_pairs = ifilter(non_empty, dir_pairs)
    if options.no_mixed:
        dir_pairs = ifilter(no_mixed, dir_pairs)
    if options.no_cbr:
        dir_pairs = ifilter(no_cbr_mp3, dir_pairs)
    if options.no_non_profile:
        dir_pairs = ifilter(profile_only_mp3, dir_pairs)
    if options.mp3_min_bit_rate != 0:
        dir_pairs = ifilter(enough_bitrate_mp3(options.mp3_min_bit_rate),
                            dir_pairs)
    if options.output_module == dnuos.output.db:
        output_db_predicate = make_output_db_predicate(options)
        dir_pairs = ifilter(output_db_predicate, dir_pairs)
    if not options.output_module == dnuos.output.db:
        dir_pairs = total_sizes(dir_pairs, data.size)
    if (not options.stripped and
        options.output_module in [dnuos.output.plaintext, dnuos.output.html]):
        dir_pairs = add_empty(dir_pairs)
    return dir_pairs


def setup_cache(cache_filename, basedirs, exclude_paths):
    """Creates and readies cache"""

    is_path_included = make_included_pred(basedirs,
                                          exclude_paths)
    is_entry_excluded = (lambda (path,), value:
                            not is_path_included(path))
    cache = PersistentDict(filename=cache_filename,
                           keep_pred=is_entry_excluded,
                           version=audiodir.Dir.__version__)
    cache.load()
    return cache


def setup_renderer(output_module, format_string, fields, options):
    """Create and readies renderer"""

    renderer = output_module.Renderer()
    renderer.format_string = format_string
    renderer.setup_columns(fields, options)
    return renderer


def main(argv=None):
    """Main entry point"""
    
    if argv is None:
        argv = sys.argv

    os.stat_float_times(False)
    warnings.formatwarning = formatwarning
    data = Data()
    options = Settings().parse_args(argv[1:])

    try:
        if options.basedirs:
            if options.use_cache:
                cache = setup_cache(
                    appdata.user_data_file('dirs.pkl',
                        options.cache_dir),
                    options.basedirs,
                    options.exclude_paths)
                adir_class = memoized(audiodir.Dir, cache)
                try:
                    appdata.create_user_data_dir(options.cache_dir)
                except IOError, err:
                    print >> sys.stderr, "Failed to create cache directory:"
                    if options.debug:
                        raise
                    print >> sys.stderr, err
                    print >> sys.stderr, ("Use the --disable-cache switch to "
                                          "disable caching")
            else:
                adir_class = audiodir.Dir

            try:
                renderer = setup_renderer(options.output_module,
                                          options.format_string,
                                          options.fields,
                                          options)
            except KeyError:
                print >> sys.stderr, ("Format string can only contain valid "
                                      "fields")
                print >> sys.stderr, ("Use the --help-output-string switch "
                                      "for more information")
                return 2

            # Append basedirs to exclude_paths to avoid traversing nested
            # basedirs again.
            adirs = make_raw_listing(options.basedirs,
                                     options.exclude_paths
                                     + options.basedirs,
                                     options.sort_key,
                                     options.merge,
                                     adir_class)
            adirs = prepare_listing(adirs, options, data)
            result = renderer.render(adirs, options, data)
        elif options.disp_version:
            result = dnuos.output.plaintext.render_version(data.version)
        else:
            print >> sys.stderr, ("No folders to process.\nType `%s -h' "
                                  "for help." % os.path.basename(argv[0]))
            return 2

        # Output
        outfile = (options.outfile and open(options.outfile, 'w')
                                   or sys.stdout)
        try:
            for chunk in result:
                print >> outfile, chunk
        except:
            # Don't evict any items if interrupted
            if options.basedirs and options.use_cache:
                cache.touch_all()
            raise
        finally:
            # Store updated cache
            if options.basedirs and options.use_cache:
                try:
                    cache.save()
                except IOError, err:
                    print >> sys.stderr, "Failed to save cache data:"
                    if options.debug:
                        raise
                    print >> sys.stderr, err
                    print >> sys.stderr, ("Use the --disable-cache switch to "
                                          "disable caching")
                    return 2
    except KeyboardInterrupt:
        print ''

def indicate_progress(dir_pairs, sizes, outs=sys.stderr):
    """Indicate progress.

    Yields an unchanged iteration of dirs with an added side effect.
    Total size in sizes is updated to stderr every step
    throughout the iteration.
    """

    for adir, root in dir_pairs:
        print >> outs, "%sB processed\r" % to_human(sizes["Total"]),
        yield adir, root 
    print >> outs, "\r               \r",


def print_bad(dir_pairs):
    """Print bad files.

    Yields an unchanged iteration of dirs with an added side effect.
    After each directory is yielded its bad files are output to
    stderr.
    """

    for adir, root in dir_pairs:
        yield adir, root
        for badfile, traceback in adir.bad_files:
            print >> sys.stderr, "Audiotype failed for:", badfile
            print >> sys.stderr, traceback


def collect_bad(dir_pairs, bad_files):
    """Collect bad files.

    Yields an unchanged iteration of dirs with an added side effect.
    After each directory is yielded its bad files are appended to
    bad_files.
    """

    for adir, root in dir_pairs:
        yield adir, root
        bad_files.extend(adir.bad_files)


def non_empty((adir, root)):
    """Empty directory predicate.

    Directories are considered empty if they contain no recognized audio files.
    """

    return adir.num_files > len(adir.bad_files)


def no_mixed((adir, root)):
    """No mixed audio directories predicate"""

    return (adir.mediatype != 'Mixed' and adir.brtype != '~' and
            len(adir.bad_files) == 0)


def no_cbr_mp3((adir, root)):
    """No CBR MP3 files predicate"""

    # This implementation does not consider CBR MP3s in Mixed directories
    return adir.mediatype != "MP3" or adir.brtype not in "C~"


def profile_only_mp3((adir, root)):
    """No non-profile MP3 predicate"""

    # This implementation does not consider non-profile MP3s in Mixed dirs
    return adir.mediatype != "MP3" or adir.profile != ""


def enough_bitrate_mp3(mp3_min_bit_rate):
    """Create low-bitrate MP3 predicate"""

    # This implementation does not consider low-bitrate MP3s in Mixed dirs
    return lambda (adir, root): (adir.mediatype != "MP3" or
                                 adir.bitrate >= mp3_min_bit_rate)


def make_output_db_predicate(options):
    """Predicate for whether something should be included in output.db"""

    artist_column = Column("A", None, None, options)
    album_column = Column("C", None, None, options)

    def output_db_predicate((adir, root)):
        return (adir.mediatype != "Mixed" and
                artist_column.get(adir) != None and
                album_column.get(adir) != None)
    return output_db_predicate


def total_sizes(dir_pairs, sizes):
    """Calculate audio file size totals.

    Yields an unchanged iteration of dirs with an added side effect.
    After each directory is yielded its filesize statistics are
    added to sizes.
    """

    for adir, root in dir_pairs:
        yield adir, root
        for mediatype, size in adir.sizes.items():
            sizes[mediatype] += size
        sizes["Total"] += adir.size


def timer_wrapper(dir_pairs, times):
    """Time the iteration.

    Yields an unchanged iteration of dirs with an added side effect.
    Time in seconds elapsed over the entire iteration is stored in times.
    """

    times['start'] = time.clock()
    for adir, root in dir_pairs:
        yield adir, root
    times['elapsed_time'] = time.clock() - times['start']


class EmptyDir(object):
    """Represent a group of merged empty directories"""

    __slots__ = ['name', 'path']

    def __init__(self, path):

        self.name = os.path.basename(path)
        self.path = path

    def __getattr__(self, attr):

        return None

    def depth_from(self, root):
        """Returns the depth from one directory to another"""

        return dir_depth(self.path) - dir_depth(root) - 1


def add_empty(dir_pairs):
    """Insert empty ancestral directories

    Pre-order directory tree traversal is assumed.
    """

    oldpath = []
    for adir, root in dir_pairs:
        path = adir.path[len(root)+1:].split(os.path.sep)
        start = equal_elements(path, oldpath)
        for depth in range(start, len(path) - 1):
            emptypath = os.path.join(root, *path[:depth+1])
            yield EmptyDir(emptypath), root
        oldpath = path

        yield adir, root


def walk2(basedir, sort_key=(lambda x: x), excluded=()):
    """Traverse a directory tree in pre-order

    Walk2 is a thin wrapper around walk. It splits each path into a
    (relpath, root) tuple where root is the parent directory of
    basedir.
    """

    root = os.path.dirname(basedir)
    for sub in walk(basedir, sort_key, excluded):
        yield sub[len(root):], root


def walk(dir_, sort_key=(lambda x: x), excluded=()):
    """Traverse a directory tree in pre-order.

    Directories are sorted by sort_key and branches specified in
    exclude are ignored. Symbolic links are followed.
    """

    subs = [os.path.join(dir_, sub)
            for sub in os.listdir(dir_)]
    subs = [sub for sub in subs
            if os.path.isdir(sub)
               and sub not in excluded]
    subs.sort(sort_key)

    yield dir_
    for sub in subs:
        for res in walk(sub, sort_key, excluded):
            yield res


def to_adir(path_pairs, constructor):
    """Converts a sequence of path pairs into a sequence of dir pairs.

    A path pair is a tuple (relpath, root). A dir pair is tuple (Dir,
    root). The Dir is validated and root is assigned to it.
    """

    for relpath, root in path_pairs:
        adir = constructor(root + relpath)
        if not adir.is_valid():
            adir.load()
        yield adir, root
