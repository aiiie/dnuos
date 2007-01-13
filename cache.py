import os
import pickle
from shutil import copy2
import stat

from attrdict import attrdict


CACHE_FILE = 'data.pkl'


class Dir(object):
    def __init__(self, path):
        self.path = path
        self.modified = os.stat(path)[stat.ST_MTIME]

    def collect(self):
        res = attrdict(
            modified=self.modified,
            children=os.listdir(self.path),
        )
        return res


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


def make_subdir_pred(base):
    """Create predicate for subdirectories of base

    >>> pred = make_subdir_pred('/usr')
    >>> pred('/home')
    False
    >>> pred('/usr/local')
    True
    >>> pred('/usr')
    True
    """
    return lambda path: is_subdir(path, base)


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
    """
    incl_preds = [ make_subdir_pred(base) for base in included ]
    excl_preds = [ make_subdir_pred(base) for base in excluded ]

    # any() is nicer than max(), but only supported by 2.5+
    return lambda path: (max(fmap(path, incl_preds)) and
                         not max(fmap(path, excl_preds)))


class Cache:
    __slots__ = ['filename', 'read', 'updates']

    def __init__(self, filename):
        self.filename = filename

    def init(self, include, exclude):
        is_path_included = make_included_pred(include, exclude)
        is_entry_included = lambda ((path, timestamp), value):
                                   is_path_included(path)
        self.read, self.updates = split_dict(self._read(), is_entry_included)

    def _read(self):
        try:
            return pickle.load(open(self.filename))
        except IOError:
            return attrdict()

    def write(self):
        try:
            copy2(self.filename, self.filename + '.bak')
        except IOError:
            pass
        pickle.dump(self.update_cache, open(self.filename, 'w'))


class cached(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    """
    def __init__(self, func, read_cache, update_cache):
        self.func = func
        self.read_cache = read_cache
        self.update_cache = update_cache

    def __call__(self, *args):
        try:
            value = self.read_cache[args]
        except KeyError:
            value = self.func(*args)
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)
        self.update_cache[args] = value
        return value

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__


def get_key(path):
    return path, os.stat(path)[stat.ST_MTIME]


def read_cache():
    try:
        return pickle.load(open(CACHE_FILE))
    except IOError:
        return attrdict()


def write_cache(cache):
    try:
        copy2(CACHE_FILE, CACHE_FILE + '.bak')
    except IOError:
        pass
    pickle.dump(cache, open(CACHE_FILE, 'w'))


def mywalk(base, exclude):
    for dirname, subdirs, files in os.walk(base):
        subdirs[:] = [ sub for sub in subdirs
                        if os.path.join(dirname, sub) not in exclude ]
        yield dirname


def main():
    # Rather lame command line parsing
    include = [ os.path.abspath(arg[1:]) for arg in sys.argv if arg[0] == '+' ]
    exclude = [ os.path.abspath(arg[1:]) for arg in sys.argv if arg[0] == '-' ]

    # Initialize cache
    is_path_included = make_included_pred(include, exclude)
    is_entry_included = lambda ((path, timestam), value): is_path_included(path)
    old_cache, new_cache = split_dict(read_cache(), is_entry_included)

    def get_value(path, timestamp):
        return Dir(path).collect()
    get_value = cached(get_value, old_cache, new_cache)

    # Traverse the base directories avoiding the excluded parts
    dirs = chain(*[ mywalk(base, exclude) for base in include ])
    for path in dirs:
        get_value(*get_key(path))

    # Print some kind of result
    print 'CACHE'
    print '\n'.join([ str(item) for item in old_cache.items() ])
    print 'UPDATED'
    print '\n'.join([ str(item) for item in new_cache.items() ])

    # Store updated and (partially) garbage collected cache
    write_cache(new_cache)


if __name__ == '__main__':
    import sys
    from itertools import chain

    main()
