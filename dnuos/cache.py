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

    Clear or otherwise modify the wkeys instance attribute to control what changes
    are tracked.
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
        """
        return dict([ (key, self[key]) for key in self.wkeys ])


class PersistentDictMetaClass(type):
    """
    Meta class for PersistentDict.
    """
    def __getitem__(cls, filename):
        """
        Get the PersistentDict instance using a specific file.
        """
        return PersistentDict.instances[filename]


class PersistentDict(UpdateTrackingDict):
    """
    A dict with persistence.
    """
    __metaclass__ = PersistentDictMetaClass

    instances = {}

    def __init__(self, *args, **kwargs):
        super(PersistentDict, self).__init__(*args, **kwargs)
        self.filename = filename = os.path.abspath(kwargs['filename'])
        if filename in PersistentDict.instances:
            raise ValueError("PersistentDict for '%s' already exists." % filename)
        PersistentDict.instances[filename] = self
        self.default = kwargs.get('default')

    # Class methods

    def writeout(cls):
        """
        Flush all instances of PersistentDict to their respective files.
        """
        for instance in PersistentDict.instances.values():
            instance._write()
    writeout = classmethod(writeout)

    # Instance methods

    def load(self, keep_pred=lambda k,v: True):
        """
        Load persistence data from file.

        Arguments:
            keep_pred - A predicate function (key, value) -> bool
                        Return values:
                            True  - This item is included in writeout (unless
                                    overwritten)
                            False - This item is excluded from writeout (unless
                                    updated)
        """
        self.clear()
        self.update(self._read())
        self.wkeys = Set([ key for key, value in self.items()
                               if keep_pred(key, value) ])

    def _read(self):
        """
        Deserialize data from file.
        """
        try:
            return pickle.load(open(self.filename))
        except IOError:
            return self.default

    def _write(self):
        """
        Serialize data to file, keeping a copy of the previous version.
        """
        try:
            copy2(self.filename, self.filename + '.bak')
        except IOError:
            pass
        pickle.dump(self.written(), open(self.filename, 'w'))


class memoized(object):
    """
    Decorator that caches a function's return value each time it is called.

    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.

    This a derivate of the one in the Python Decorator Library:
    http://wiki.python.org/moin/PythonDecoratorLibrary
    It has been changed to take the cache mapping as an argument and to store
    the result on both cache misses and cache hits.
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


class cached(memoized):
    def __init__(self, func, filename):
        cache = PersistentDict(filename=filename, default={})
        super(cached, self).__init__(func, cache)
