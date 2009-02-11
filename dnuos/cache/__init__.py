"""A module for caching"""

try:
    from dnuos.cache.sqlitecache import Cache
except ImportError:
    from dnuos.cache.shelvecache import Cache


def memoized(func, cache):
    """A decorator that caches a function's return value each time it's called.

    If called later with the same argument, the cached value is
    returned, and not re-evaluated.

    The function must only take one argument: a string.

    Example usage and behavior:

    >>> def fake_dir(path):
    ...     print 'fake_dir()'
    ...     return '[dir data]'
    ...
    >>> cache = {'/old/dir': '[old dir data]'}
    >>> fake_dir = memoized(fake_dir, cache)
    >>> fake_dir('/dev/null')
    fake_dir()
    '[dir data]'
    >>> cache['/old/dir']
    '[old dir data]'
    >>> fake_dir('/dev/null')
    '[dir data]'
    """

    def wrapper(key):
        """Wrapper function"""

        try:
            return cache[key]
        except KeyError:
            value = func(key)
            cache[key] = value
            return value

    return wrapper
