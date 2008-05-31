"""UTF-8 drop-in replacements for various os.path functions.

Dnuos has always assumed UTF-8 as the file system encoding, but this isn't
always the case, especially on Windows. These functions take UTF-8 strings,
decode them to unicode objects, and pass them to the underlying os.path
functions. Any functions that return paths with unicode objects are
encoded back into UTF-8 strings.

This has the effect that UTF-8 can be used even if the file system uses
a different encoding, due to decoding to unicode beforehand.
"""

import os


def listdir(path):

    paths = []
    for p in os.listdir(path.decode('utf-8')):
        # Don't encode paths that aren't Unicode. os.listdir will return str
        # objects for any paths it couldn't decode to unicode objects (see
        # http://bugs.python.org/issue683592).
        if isinstance(p, unicode):
            paths.append(p.encode('utf-8'))
        else:
            paths.append(p)
    return paths


def _wrap(func):

    def wrapper(path, *args, **kw):
        try:
            return func(path.decode('utf-8'), *args, **kw)
        except UnicodeError:
            return func(path, *args, **kw)
    return wrapper


exists = _wrap(os.path.exists)
expanduser = _wrap(os.path.expanduser)
getmtime = _wrap(os.path.getmtime)
getsize = _wrap(os.path.getsize)
isdir = _wrap(os.path.isdir)
isfile = _wrap(os.path.isfile)
mkdir = _wrap(os.mkdir)
makedirs = _wrap(os.makedirs)
normpath = _wrap(os.path.normpath)
rename = _wrap(os.rename)
remove = _wrap(os.remove)
rmdir = _wrap(os.rmdir)
open = _wrap(open)
