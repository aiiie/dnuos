"""A module for caching"""

import os
try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    set
except NameError:
    from sets import Set as set


class UpdateTrackingDict(dict):
    """
    A dict that tracks what items have been updated.

    Keeps track of what entries have been (over)written since
    construction or since last call to clear_written. Old values are
    not kept, but the subset of written entries can be obtained
    through the written-method.
    """

    def __init__(self, *args, **kwargs):

        super(UpdateTrackingDict, self).__init__(*args, **kwargs)
        self.wkeys = set()

    def __setitem__(self, key, value):

        super(UpdateTrackingDict, self).__setitem__(key, value)
        self.wkeys.add(key)

    def __delitem__(self, key):

        super(UpdateTrackingDict, self).__delitem__(key)
        self.wkeys.discard(key)

    def clear(self):
        """Removes all items"""

        super(UpdateTrackingDict, self).clear()
        self.wkeys.clear()

    def update(self, other):
        """Updates items from other dict"""

        super(UpdateTrackingDict, self).update(other)
        self.wkeys |= set(other.keys())

    def written(self):
        """Get a dict of all updated items.

        The returned dict contains the subset of updated items in
        self.
        """

        return dict([(key, self[key]) for key in self.wkeys])

    def clear_written(self):
        """Clear the memory of updated entries"""

        self.wkeys.clear()

    def touch(self, key):
        """Make a dict entry appear updated"""

        self.wkeys.add(key)

    def touch_all(self):
        """Update all dict entries"""

        self.wkeys = set(self.keys())


class PersistentDict(UpdateTrackingDict):
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
            keep_pred - A predicate function (args, result) -> bool.
                        This is used at loading to control what
                        entries are to be presistent through
                        subsequent saves. Entries that are updated
                        between load and save will persist in any
                        case.
                        When the predicate returns True, the entry
                        will persist.
                        When the predicate returns False, the entry
                        will be dropped unless it's been updated.
        """

        keep_pred = kwargs.pop('keep_pred', (lambda k, v: True))
        self.filename = kwargs.pop('filename')
        self.version = kwargs.pop('version')
        self.checksum = None
        super(PersistentDict, self).__init__(*args, **kwargs)

        try:
            file_ = open(self.filename, 'rb')
            try:
                version = pickle.load(file_)
                self.checksum = pickle.load(file_)
                if version == self.version:
                    self.update(pickle.load(file_))
            finally:
                file_.close()
        except IOError:
            pass

        self.clear_written()
        for key, value in self.iteritems():
            if keep_pred(key, value):
                self.touch(key)

    def save(self):
        """Serialize data to file"""

        written = self.written()
        checksum = hash(tuple([d.modified for d in written.itervalues()]))
        if checksum != self.checksum:
            file_ = open(self.filename, 'wb')
            try:
                pickle.dump(self.version, file_, 2)
                pickle.dump(checksum, file_, 2)
                pickle.dump(self.written(), file_, 2)
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

    def __init__(self, func, cache=None):
        self.func = func
        if cache is None:
            cache = {}
        self.cache = cache

    def __call__(self, *args):
        try:
            value = self.cache[args]
            return value
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)

    def __repr__(self):
        """Return the function's docstring."""

        return self.func.__doc__
