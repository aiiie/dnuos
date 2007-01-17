import os
import stat

import app
from attrdict import attrdict
from cache import Cache
from cache import cached
from misc import make_included_pred


CACHE_FILE = app.user_data_file('dirs.pkl')


class Dir(object):
    def __init__(self, path):
        self.path = path
        self.modified = os.stat(path)[stat.ST_MTIME]

    def collect(self):
        print "COLLECT:", self.path
        res = attrdict(
            modified=self.modified,
            children=os.listdir(self.path),
        )
        return res


def get_dir(path, timestamp, children):
    return Dir(path).collect()
get_dir = cached(get_dir, Cache(CACHE_FILE))


def get_dir_cache_key(path):
    return path, os.stat(path)[stat.ST_MTIME], tuple(os.listdir(path))

def mywalk(base, exclude):
    for dirname, subdirs, files in os.walk(base):
        subdirs[:] = [ sub for sub in subdirs
                        if os.path.join(dirname, sub) not in exclude ]
        yield get_dir_cache_key(dirname)


def main():
    # Rather lame command line parsing
    include = [ os.path.abspath(arg[1:]) for arg in sys.argv if arg[0] == '+' ]
    exclude = [ os.path.abspath(arg[1:]) for arg in sys.argv if arg[0] == '-' ]

    # Initialize cache
    is_path_included = make_included_pred(include, exclude)
    is_entry_excluded = lambda ((path, timestamp, files), value): \
                               not is_path_included(path)
    Cache.setup(treat_as_update=is_entry_excluded)

    # Traverse the base directories avoiding the excluded parts
    dir_cache_keys = chain(*[ mywalk(base, exclude) for base in include ])
    for dir_cache_key in dir_cache_keys:
        print get_dir(*dir_cache_key)

    # Write out updated and (partially) garbage collected cache
    #app.create_user_data_dir()
    #Cache.writeout()


if __name__ == '__main__':
    import sys
    from itertools import chain

    main()
