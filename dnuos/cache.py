"""A module for caching"""

import os
import shelve

class PersistentDict(shelve.Shelf, object):
    """A dict with persistence.

    A wrapper around UpdateTrackingDict that adds the ability to
    pickle written entries to and from a file. A predicate function
    can be specified to control what entries to keep from a load to the
    following save.
    """
    def __init__(self, *args, **kwargs):
        """Construct a new PersistentDict instance.

        This just stores the specified arguments. Call the load method
        to initialize.

        Arguments:
            filename  - The persistence data file for loading and
                        saving.
        """

        import anydbm
        super(PersistentDict, self).__init__(
            anydbm.open(kwargs['filename'], 'c'),
            protocol=2)

        self.written = []
        self.version = kwargs.pop('version')
        old_version = self.pop('__version__', None)
        if old_version != self.version:
            self.clear()

    def save(self):
        """Serialize data to file"""

        for path in self.iterkeys():
            if path not in self.written and not os.path.isdir(path):
                del self[path]

        self['__version__'] = self.version
        self.close()


class memoized(object):
    """Decorator that caches a function's return value each time it's called.

    If called later with the same argument, the cached value is
    returned, and not re-evaluated.

    The function must only take one argument. This argument is appended to
    the list in cache.written, so persisted and fresh data can be
    differentiated.

    Example usage and behavior:

    >>> def fake_dir(path):
    ...     print 'fake_dir()'
    ...     return '[dir data]'
    ...
    >>> class MemoCache(dict):
    ...     def __init__(self, *args, **kwargs):
    ...         super(MemoCache, self).__init__(*args, **kwargs)
    ...         self.written = []
    ...
    >>> cache = MemoCache({'/old/dir': '[old dir data]'})
    >>> fake_dir = memoized(fake_dir, cache)
    >>> fake_dir('/dev/null')
    fake_dir()
    '[dir data]'
    >>> cache.written
    ['/dev/null']
    >>> cache['/old/dir']
    '[old dir data]'
    >>> fake_dir('/dev/null')
    '[dir data]'
    """

    def __init__(self, func, cache):
        self.func = func
        self.cache = cache

    def __call__(self, path):
        try:
            value = self.cache[path]
        except KeyError:
            value = self.func(path)
            self.cache[path] = value
        self.cache.written.append(path)
        return value
