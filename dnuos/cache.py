"""A module for caching"""

import os
try:
    import cPickle as pickle
except ImportError:
    import pickle

class PersistentDict(dict):
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

        self.filename = kwargs.pop('filename')
        self.version = kwargs.pop('version')
        self.written = []
        super(PersistentDict, self).__init__(*args, **kwargs)

        try:
            file_ = open(self.filename, 'rb')
            try:
                version = pickle.load(file_)
                if version == self.version:
                    self.update(pickle.load(file_))
            finally:
                file_.close()
        except IOError:
            pass

    def save(self):
        """Serialize data to file"""

        for path in self.iterkeys():
            if path not in self.written and not os.path.isdir(path):
                del self[path]

        file_ = open(self.filename, 'wb')
        try:
            pickle.dump(self.version, file_, 2)
            pickle.dump(self, file_, 2)
        finally:
            file_.close()


class memoized(object):
    """Decorator that caches a function's return value each time it's called.

    If called later with the same arguments, the cached value is
    returned, and not re-evaluated.

    This a derivate of the memoized decorator in the Python Decorator
    Library: http://wiki.python.org/moin/PythonDecoratorLibrary
    It has been changed to take the cache mapping as an argument and
    to store the result on cache misses as well as cache hits.
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
