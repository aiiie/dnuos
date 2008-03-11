"""A module for caching"""

import os
import shelve

class PersistentDict(shelve.Shelf, object):
    """A dict with persistence, based on shelve.Shelf"""

    def __init__(self, filename, version):
        """Construct a new PersistentDict instance"""

        import anydbm
        super(PersistentDict, self).__init__(
            anydbm.open(filename, 'c'),
            protocol=2)

        self.version = version
        old_version = self.pop('__version__', None)
        if old_version != self.version:
            self.clear()

    def cull(self):
        """Removes bad directories and returns count"""

        paths = [p for p in self.iterkeys() if not os.path.isdir(p)]
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

    The function must only take one argument.

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
