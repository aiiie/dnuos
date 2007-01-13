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


def split_cache(cache, pred):
    """Split the cache in two by a predicate function
    """
    cells = partition(cache.items(),
                      lambda ((path, timestamp), value): pred(path))
    return dict(cells.get(True, [])), dict(cells.get(False, []))


def cache_lookup(dirs, old_cache, new_cache):
    """Get lookups from cache or calculate and put them in cache
    """
    for adir in dirs:
        key = (adir.path, adir.modified)
        data = old_cache.get(key) or adir.collect()
        new_cache[key] = data
        yield data


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
        yield Dir(dirname)


if __name__ == '__main__':
    import sys
    from itertools import chain

    # Rather lame command line parsing
    include = [ os.path.abspath(arg[1:]) for arg in sys.argv if arg[0] == '+' ]
    exclude = [ os.path.abspath(arg[1:]) for arg in sys.argv if arg[0] == '-' ]

    # Initialize cache
    is_included = make_included_pred(include, exclude)
    old_cache, new_cache = split_cache(read_cache(), is_included)

    # Traverse the base directories avoiding the excluded parts
    dirs = chain(*[ mywalk(base, exclude) for base in include ])
    dirs = cache_lookup(dirs, old_cache, new_cache)
    for path in dirs:
        pass

    # Print some kind of result
    print 'CACHE'
    print '\n'.join([ str(item) for item in old_cache.items() ])
    print 'UPDATED'
    print '\n'.join([ str(item) for item in new_cache.items() ])

    # Store updated and (partially) garbage collected cache
    write_cache(new_cache)
