"""A module for caching"""

import os
import shelve
import sys

import dnuos.path

def update_from_1_0(cache):
    """Updates a 1.0 version cache to the current version"""

    for key, adir in cache.iteritems():
        adir._types = tuple(adir._types)
        for attr in ('artists', 'albums', '_profiles'):
            setattr(adir, attr,
                    dict([(k, tuple(v)) for (k, v) in
                          getattr(adir, attr).iteritems()]))
        cache[key] = adir


updates = {'1.0': update_from_1_0}


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

        paths = [p.decode('utf-8') for p in self.iterkeys()
                 if not dnuos.path.isdir(p)]
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
