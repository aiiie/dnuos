# -*- coding: iso-8859-1 -*-
#
# A module for gathering information about a directory of audio files
#
# This program is under GPL license. See COPYING file for details.
#
# Copyright 2007
# Mattias Päivärinta <pejve@vasteras2.net>

import os
import pickle
from sets import Set
from shutil import copy2

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
        self.wkeys = Set()

    def __set__(self, value):
        super(UpdateTrackingDict, self).__set__(value)
        self.wkeys = Set(value.keys())

    def __setitem__(self, key, value):
        super(UpdateTrackingDict, self).__setitem__(key, value)
        self.wkeys.add(key)

    def clear(self):
        super(UpdateTrackingDict, self).clear()
        self.wkeys.clear()

    def update(self, other):
        super(UpdateTrackingDict, self).update(other)
        self.wkeys |= Set(other.keys())

    def written(self):
        """
        Get a dict of all updated items.

        The returned dict contains the subset of updated items in
        self.
        """
        return dict([ (key, self[key]) for key in self.wkeys ])


class PersistentDict(UpdateTrackingDict):
    """
    A dict with persistence.
  
    A wrapper around UpdateTrackingDict that adds the ability to
    pickle written entries to and from a file. A predicate function
    can be specified to decide what entries to keep from a load to the
    following save.
    """
    def __init__(self, *args, **kwargs):
        super(PersistentDict, self).__init__(*args, **kwargs)
        self.filename = filename = os.path.abspath(kwargs['filename'])
        self.default = kwargs.get('default')

    # Instance methods

    def load(self, keep_pred=lambda k,v: True):
        """
        Arguments:
            filename  -
            default   -
            keep_pred - A predicate function (key, value) -> bool
                        Return values:
                            True  - This item is included in writeout
                                    (unless overwritten)
                            False - This item is excluded from writeout
                                    (unless updated)
        """
        self.clear()
        self.update(self._read())
        self.wkeys = Set([ key for key, value in self.items()
                               if keep_pred(key, value) ])

    def _read(self):
        """
        Deserialize data from file.

        Clear previous contents, deserialize data from file and update
        written-status according as per the predicate function.
        If deserialisation fails for whatever reason the default dict
        is used for initialization.
        """
        try:
            return pickle.load(open(self.filename))
        except IOError:
            return self.default

    def flush(self):
        """
        Serialize data to file.

        Serialize data to file, keeping a copy of the previous version.
        """
        try:
            copy2(self.filename, self.filename + '.bak')
        except IOError:
            pass
        pickle.dump(self.written(), open(self.filename, 'w'))


class memoized(object):
    """
    Decorator that caches a function's return value each time it is
    called.

    If called later with the same arguments, the cached value is
    returned, and not re-evaluated.

    This a derivate of the one in the Python Decorator Library:
    http://wiki.python.org/moin/PythonDecoratorLibrary
    It has been changed to take the cache mapping as an argument and
    to store the result on both cache misses and cache hits.
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
