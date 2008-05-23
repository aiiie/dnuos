"""A module for caching"""

import shelve
import sys

import dnuos.path

def has_flac(adir):
    """Returns whether or not an audiodir has FLAC files.

    FLAC files scanned prior to 1.0.6 don't have album/artist set, so they
    need to be invalidated from the cache to get scanned again.
    """

    return 'FLAC' in adir._types


def update_from_1_0(cache):
    """Updates a 1.0 version cache to the current version"""

    fsenc = sys.getfilesystemencoding().lower()
    bad_items = []

    for key, adir in cache.iteritems():
        # Invalidate FLAC audiodirs
        if has_flac(adir):
            bad_items.append(key)
            continue

        # Convert paths to UTF-8
        if fsenc != 'utf-8':
            try:
                adir.path = adir.path.decode(fsenc).encode('utf-8')
                adir._audio_files = [p.decode(fsenc).encode('utf-8') for p in
                                     adir._audio_files]
                adir._bad_files = [(p.decode(fsenc).encode('utf-8'), tb)
                                   for (p, tb) in adir._bad_files]
            except UnicodeError:
                bad_items.append(key)
                continue

        # Convert set() instances to tuples
        adir._types = tuple(adir._types)
        for attr in ('artists', 'albums', '_profiles'):
            setattr(adir, attr,
                    dict([(k, tuple(v)) for (k, v) in
                          getattr(adir, attr).iteritems()]))

        cache[key] = adir

    # Remove items that couldn't be updated
    for key in bad_items:
        del cache[key]


def update_from_1_0_4(cache):
    """Updates a 1.0.4 version cache to the current version"""

    # All paths should remain the same on UTF-8 file systems
    fsenc = sys.getfilesystemencoding().lower()
    if fsenc == 'utf-8':
        return

    import itertools
    bad_items = []

    for key, adir in cache.iteritems():
        # Invalidate FLAC audiodirs
        if has_flac(adir):
            bad_items.append(key)
            continue

        try:
            # Try re-encoding from the native encoding to UTF-8
            path = adir.path.decode(fsenc).encode('utf-8')
            audio_files = [p.decode(fsenc).encode('utf-8') for p in
                           adir._audio_files]
            bad_files = [(p.decode(fsenc).encode('utf-8'), tb) for (p, tb) in
                         adir._bad_files]
            if (path != adir.path or audio_files != adir._audio_files or
                bad_files != adir._bad_files):
                # The paths differ, so see if the converted paths actually exist
                for p in itertools.chain([path], audio_files, bad_files):
                    if not dnuos.path.exists(p):
                        raise UnicodeError()

                adir.path = path
                adir._audio_files = audio_files
                adir._bad_files = bad_files
                cache[key] = adir
        except UnicodeError:
            bad_items.append(key)

    # Remove any items that couldn't be converted. Directories that actually
    # exist but couldn't be converted will just get scanned again.
    for key in bad_items:
        del cache[key]


def update_from_1_0_5(cache):
    """Updates a 1.0.5 version cache to the current version"""

    # Invalidate FLAC audiodirs
    for key in [key for (key, adir) in cache.iteritems() if has_flac(adir)]:
        del cache[key]


updates = {'1.0': update_from_1_0,
           '1.0.4': update_from_1_0_4,
           '1.0.5': update_from_1_0_5}


class PersistentDict(shelve.Shelf, object):
    """A dict with persistence, based on shelve.Shelf"""

    def __init__(self, filename, version):
        """Construct a new PersistentDict instance"""

        filename = filename.decode('utf-8')
        filename = filename.encode(sys.getfilesystemencoding())

        import anydbm
        super(PersistentDict, self).__init__(
            anydbm.open(filename, 'c'),
            protocol=2)

        self.version = version
        old_version = self.pop('__version__', None)
        if old_version != self.version:
            if old_version in updates:
                updates[old_version](self)
            else:
                self.clear()

    def cull(self):
        """Removes bad directories and returns count"""

        paths = [p for p in self.iterkeys() if not dnuos.path.isdir(p)]
        for path in paths:
            del self[path]
        return len(paths)

    def save(self):
        """Serializes data to file"""

        self['__version__'] = self.version
        self.close()


def memoized(func, cache):
    """A decorator that caches a function's return value each time it's called.

    If called later with the same argument, the cached value is
    returned, and not re-evaluated.

    The function must only take one argument: a string.

    Example usage and behavior:

    >>> def fake_dir(path):
    ...     print 'fake_dir()'
    ...     return '[dir data]'
    ...
    >>> cache = {'/old/dir': '[old dir data]'}
    >>> fake_dir = memoized(fake_dir, cache)
    >>> fake_dir('/dev/null')
    fake_dir()
    '[dir data]'
    >>> cache['/old/dir']
    '[old dir data]'
    >>> fake_dir('/dev/null')
    '[dir data]'
    """

    def wrapper(key):
        """Wrapper function"""

        try:
            return cache[key]
        except KeyError:
            value = func(key)
            cache[key] = value
            return value

    return wrapper
