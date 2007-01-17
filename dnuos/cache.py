import os
import pickle
from shutil import copy2

from misc import fmap
from misc import is_subdir
from misc import split_dict


class Cache(object):
    __slots__ = ['filename', 'read', 'updates']

    instances = []

    def __init__(self, filename):
        Cache.instances.append(self)
        self.filename = filename

    def setup(cls, treat_as_update=lambda entry: False):
        for instance in cls.instances:
            instance._setup(treat_as_update)
    setup = classmethod(setup)

    def writeout(cls):
        for instance in cls.instances:
            instance._write()
    writeout = classmethod(writeout)

    def _setup(self, treat_as_update):
        self.updates, self.read = split_dict(self._read(), treat_as_update)

    def _read(self):
        try:
            return pickle.load(open(self.filename))
        except IOError:
            return {}

    def _write(self):
        try:
            copy2(self.filename, self.filename + '.bak')
        except IOError:
            pass
        pickle.dump(self.updates, open(self.filename, 'w'))


class cached(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    """
    __slots__ = ['func', 'cache']

    def __init__(self, func, cache):
        self.func = func
        self.cache = cache

    def __call__(self, *args):
        try:
            value = self.cache.read[args]
        except KeyError:
            value = self.func(*args)
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)
        self.cache.updates[args] = value
        return value

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__
