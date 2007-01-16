import os
import pickle
from shutil import copy2


def partition(iterable, func):
    """Partition a set of objects into equivalence classes

    Returns a dictionary { func(obj): [equivalent objects] }
    Object o1 and o2 are equivalent if and only if func(o1) == func(o2)

    >>> p = partition(range(0, 10), lambda x: x % 3)

    >>> classes = p.keys()
    >>> classes.sort()
    >>> print classes
    [0, 1, 2]

    >>> print p[0], p[1], p[2]
    [0, 3, 6, 9] [1, 4, 7] [2, 5, 8]
    """
    partitions = { }
    for obj in iterable:
        partitions.setdefault(func(obj), []).append(obj)
    return partitions


def split_dict(dct, pred):
    """Split dictionary in two by a predicate function

    >>> dct = {1:'a', 2:'b', 3:'c'}
    >>> pred = lambda (key, value): key % 2 == 0
    >>> t, f = split_dict(dct, pred)
    >>> t
    {2: 'b'}
    >>> print len(f), 1 in f, 3 in f
    2 True True
    """
    cells = partition(dct.items(), pred)
    return dict(cells.get(True, [])), dict(cells.get(False, []))


def fmap(value, funcs):
    """Feeds the same value to a list of functions

    >>> fmap(-5.5, [str, int, abs])
    ['-5.5', -5, 5.5]
    """
    return [ func(value) for func in funcs ]


def is_subdir(path1, path2):
    """Returns True if path1 is a subdirectory of path2, otherwise False
    
    >>> is_subdir('/home', '/usr')
    False
    >>> is_subdir('/usr/local', '/usr')
    True
    >>> is_subdir('/usr', '/usr')
    True
    """
    path1 = path1.split(os.path.sep)
    path2 = path2.split(os.path.sep)
    return path2 == path1[:len(path2)]


def make_included_pred(included, excluded):
    """Create predicate for included but not excluded paths
    
    >>> pred = make_included_pred(['/etc','/usr'], ['/usr/local'])
    >>> pred('/usr/local')
    False
    >>> pred('/usr/local/share')
    False
    >>> pred('/usr')
    True
    >>> pred('/usr/doc')
    True
    >>> pred('/home')
    False

    >>> pred = make_included_pred([], ['/usr/local'])
    >>> pred('/')
    False

    >>> pred = make_included_pred(['/usr'], [])
    >>> pred('/usr/local/share')
    True
    """
    i_preds = [ lambda path, base=base: is_subdir(path, base)
                for base in included ]
    e_preds = [ lambda path, base=base: is_subdir(path, base)
                for base in excluded ]

    # any() is nicer than max(), but only supported by 2.5+
    return lambda path: ((bool(included) and max(fmap(path, i_preds))) and not
                         (bool(excluded) and max(fmap(path, e_preds))))


class Cache(object):
    __slots__ = ['filename', 'read', 'updates']

    instances = []

    def __init__(self, filename):
        Cache.register(self)
        self.filename = filename

    def register(cls, instance):
        cls.instances.append(instance)
    register = classmethod(register)

    def setup(cls, include, exclude):
        for instance in cls.instances:
            instance._setup(include, exclude)
    setup = classmethod(setup)

    def writeout(cls):
        for instance in cls.instances:
            instance._write()
    writeout = classmethod(writeout)

    def _setup(self, include, exclude):
        is_path_included = make_included_pred(include, exclude)
        is_entry_included = lambda ((path, timestamp), value): \
                                   is_path_included(path)
        self.read, self.updates = split_dict(self._read(), is_entry_included)

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
