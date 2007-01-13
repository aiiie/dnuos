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


def fmap(value, funcs):
    """Feeds the same value to a list of functions

    >>> fmap(-5.5, [str, int, abs])
    ['-5.5', -5, 5.5]
    """
    return map(lambda f: f(value), funcs)


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
    incl_preds = map(lambda base: make_subdir_pred(base), included)
    excl_preds = map(lambda base: make_subdir_pred(base), excluded)

    # any() is nicer than max(), but only supported by 2.5+
    return lambda path: (max(fmap(path, incl_preds)) and
                         not max(fmap(path, excl_preds)))


def get_outside(cache, include, exclude):
    """Return the parts of cache that are outside the current domain
    """
    is_included = make_included_pred(include, exclude)
    return [ ((path, timestamp), value)
             for (path, timestamp), value in cache.items()
             if not is_included(path) ]


def cache_lookup(dirs, cache, updates):
    """Get lookups from cache or calculate and put them in cache
    """
    for adir in dirs:
        key = (adir.path, adir.modified)
        data = cache.get(key) or adir.collect()
        updates[key] = data
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


def mywalk(base):
    for dirname, subdirs, files in os.walk(base):
        yield Dir(dirname)


if __name__ == '__main__':
    import sys
    from itertools import chain

    # Rather lame command line parsing
    include = [ os.path.abspath(arg[1:]) for arg in sys.argv if arg[0] == '+' ]
    exclude = [ os.path.abspath(arg[1:]) for arg in sys.argv if arg[0] == '-' ]

    # Initialize cache
    cache = read_cache()
    updated = {}

    # Traverse the base directories avoiding the excluded parts
    dirs = chain(*map(mywalk, include))
    dirs = cache_lookup(dirs, cache, updated)
    for path in dirs:
        pass

    # Print some kind of result
    print 'CACHE'
    print '\n'.join(map(str, cache.items()))
    print 'UPDATED'
    print '\n'.join(map(str, updated.items()))

    # Store updated and (partially) garbage collected cache
    updated.update(get_outside(cache, include, exclude))
    write_cache(updated)
