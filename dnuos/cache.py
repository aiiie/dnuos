"""A module for caching"""

import os
try:
    import cPickle as pickle
except ImportError:
    import pickle
import sys
from shutil import copy2

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
        del self.wkeys[key]

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

        self.wkeys = self.keys()


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
            default   - Data to be used if the loading of the data
                        file fails for whatever reason.
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

        super(PersistentDict, self).__init__(*args, **kwargs)
        self.version = kwargs['version']
        self.filename = os.path.abspath(kwargs['filename'])
        self.default = kwargs.get('default', {})
        self.keep_pred = kwargs.get('keep_pred', lambda k,v: True)
        self.checksum = None


    def load(self):
        """Deserialize data from file.

        Clear previous contents, deserialize data from file and update
        written-status according as per the predicate function.
        If deserialisation fails for whatever reason the default dict
        is used for initialization.
        """

        try:
            f = open(self.filename, 'rb')
            try:
                version = pickle.load(f)
                self.checksum = pickle.load(f)
                if version != self.version:
                    raise ValueError()
                data = pickle.load(f)
            finally:
                f.close()
        except StandardError:
            data = self.default
        self.clear()
        self.update(data)
        self.clear_written()
        for key, value in self.items():
            if self.keep_pred(key, value):
                self.touch(key)

    def save(self):
        """Serialize data to file"""

        checksum = hash(tuple([d.modified for d in self.written().values()]))
        if checksum != self.checksum:
            f = open(self.filename, 'wb')
            pickle.dump(self.version, f, 2)
            pickle.dump(checksum, f, 2)
            pickle.dump(self.written(), f, 2)
            f.close()


class memoized(object):
    """Decorator that caches a function's return value each time it's called.

    If called later with the same arguments, the cached value is
    returned, and not re-evaluated.

    This a derivate of the memoized decorator in the Python Decorator
    Library: http://wiki.python.org/moin/PythonDecoratorLibrary
    It has been changed to take the cache mapping as an argument and
    to store the result on cache misses as well as cache hits.
    """

    def __init__(self, func, cache={}):
        self.func = func
        self.cache = cache

    def __call__(self, *args):
        try:
            value = self.cache[args]
        except KeyError:
            value = self.func(*args)
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)
        self.cache[args] = value
        return value

    def __repr__(self):
        """Return the function's docstring."""

        return self.func.__doc__
