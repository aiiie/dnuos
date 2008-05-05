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

    return [p.encode('utf-8') for p in os.listdir(path.decode('utf-8'))]


def _wrap(func):

    return lambda path, *args, **kw: func(path.decode('utf-8'), *args, **kw)


exists = _wrap(os.path.exists)
getmtime = _wrap(os.path.getmtime)
getsize = _wrap(os.path.getsize)
isdir = _wrap(os.path.isdir)
isfile = _wrap(os.path.isfile)
makedirs = _wrap(os.makedirs)
remove = _wrap(os.remove)
rmdir = _wrap(os.rmdir)
open = _wrap(open)
