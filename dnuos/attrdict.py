class attrdict(dict):
    """A dict whose items can also be accessed as member variables.

    >>> d = attrdict(a=1, b=2)
    >>> d['c'] = 3
    >>> print d.a, d.b, d.c
    1 2 3

    >>> print d['a']
    1

    >>> d['get'] = None
    >>> print type(d.get)
    <type 'builtin_function_or_method'>

    >>> import pickle
    >>> d = pickle.loads(pickle.dumps(d))
    >>> print d.a, d.b, d.c
    1 2 3
    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __getattr__(self, name):
        return self[name]

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, dct):
        self.__dict__.update(dct)
