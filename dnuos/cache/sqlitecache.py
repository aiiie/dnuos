"""sqlite3-based cache"""

import sqlite3
import sys
from UserDict import DictMixin

try:
    import cPickle as pickle
except ImportError:
    import pickle

import dnuos.path

class Cache(object, DictMixin):
    """A dict with persistence, backed by sqlite3"""

    def __init__(self, filename, version):

        filename = filename.decode('utf-8')
        filename = filename.encode(sys.getfilesystemencoding())
        filename = '.'.join([filename, version, 'sqlite'])

        self._conn = sqlite3.connect(filename)
        c = self._conn.cursor()
        try:
            c.execute('create table if not exists dirs '
                      '(path text unique, dir blob)')
            self._conn.commit()
        finally:
            c.close()

        self.version = version

    def __getitem__(self, key):

        key = key.decode('utf-8')
        c = self._conn.cursor()
        try:
            c.execute('select dir from dirs where path = ? limit 1', (key,))
            row = c.fetchone()
            if not row:
                raise KeyError()
            else:
                return pickle.loads(str(row[0]))
        finally:
            c.close()

    def __setitem__(self, key, value):

        key = key.decode('utf-8')
        c = self._conn.cursor()
        try:
            c.execute('replace into dirs values (?, ?)',
                      (key, buffer(pickle.dumps(value, 2))))
            self._conn.commit()
        finally:
            c.close()

    def __delitem__(self, key):

        key = key.decode('utf-8')
        c = self._conn.cursor()
        try:
            c.execute('delete from dirs where path = ?', (key,))
            self._conn.commit()
            if c.rowcount == 0:
                raise KeyError()
        finally:
            c.close()

    def keys(self):

        c = self._conn.cursor()
        try:
            c.execute('select path from dirs')
            paths = []
            row = c.fetchone()
            while row:
                paths.append(row[0])
                row = c.fetchone()
            return paths
        finally:
            c.close()

    def cull(self):
        """Removes bad directories and returns count"""

        paths = []
        c = self._conn.cursor()
        try:
            c.execute('select path from dirs')
            while True:
                row = c.fetchone()
                if not row:
                    break
                if not dnuos.path.isdir(row[0]):
                    paths.append(row[0])
        finally:
            c.close()

        for path in paths:
            del self[path]

        c = self._conn.cursor()
        try:
            c.execute('vacuum')
        finally:
            c.close()

        return len(paths)

    def save(self):
        """Serializes data to file"""

        self._conn.close()
