"""shelve-based cache"""

import shelve
import sys

import dnuos.path

updates = {}

class Cache(shelve.Shelf, object):
    """A dict with persistence, based on shelve.Shelf"""

    def __init__(self, filename, version):
        """Construct a new PersistentDict instance"""

        filename = filename.decode('utf-8')
        filename = filename.encode(sys.getfilesystemencoding())

        import dumbdbm
        super(Cache, self).__init__(
            dumbdbm.open(filename, 'c'),
            protocol=2)

        self.version = version
        old_version = self.pop('__version__', None)
        if old_version != self.version:
            if old_version in updates:
                updates[old_version](self)
            else:
                self.clear()

    def cull(self):
        """Removes bad directories and returns count"""

        paths = [p for p in self.iterkeys() if not dnuos.path.isdir(p)]
        for path in paths:
            del self[path]
        return len(paths)

    def save(self):
        """Serializes data to file"""

        self['__version__'] = self.version
        self.close()
