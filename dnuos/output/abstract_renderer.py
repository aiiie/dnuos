import string
from dnuos.misc import to_human
import dnuos.conf


class AbstractRenderer(object):
    def set_fields(self, fields):
        self.columns = map(parse_field, fields)


class Column(object):
    formatter_table = {
        "b": lambda data, depth: to_human(data, 1000.0),
        "l": lambda data, depth: to_minutes(data),
        "m": lambda data, depth: time.ctime(data),
        "n": lambda data, depth: dnuos.conf.Settings().indent(data, depth),
        "s": lambda data, depth: to_human(data),
    }
    attr_table = {
        "a": ('audiolist_format', 'Bitrate(s)'),
        "A": ('artist', 'Artist'),
        "b": ('bitrate', 'Bitrate'),
        "B": ('bitrate', 'Bitrate'),
        "C": ('album', 'Album'),
        #"d": "Dir",
        "D": ('depth', 'Depth'),
        "f": ('num_files', 'Files'),
        "l": ('length', 'Length'),
        "L": ('length', 'Length'),
        "m": ('modified', 'Modified'),
        "M": ('modified', 'Modified'),
        "n": ('name', 'Album/Artist'),
        "N": ('name', 'Album/Artist'),
        "p": ('profile', 'Profile'),
        "P": ('path', 'Path'),
        "q": ('quality', 'Quality'),
        "s": ('size', 'Size'),
        "S": ('size', 'Size'),
        "t": ('mediatype', 'Type'),
        "T": ('brtype', 'BR Type'),
    }

    def __init__(self, tag, width, suffix):
        self.width, self.suffix = width, suffix
        if tag in self.formatter_table:
            self.formatter = self.formatter_table[tag]
        else:
            self.formatter = lambda x,y: x
        self.attr, self.name = self.attr_table[tag]

    def _format(self, data, suffixes):
        if suffixes:
            if data:
                data += self.suffix
            else:
                data = ' ' * len(self.suffix)
        if self.width != None:
            data = "%*.*s" % (self.width, abs(self.width), data)
        return data

    def header(self, suffixes=True):
        return self._format(self.name, suffixes)

    def get(self, adir):
        return getattr(adir, self.attr)

    def get_formatted(self, adir, root, suffixes=True):
        data = self.get(adir)
        if data is None:
            data = ''
        else:
            data = self.formatter(data, adir.depth_from(root))
        return self._format(data, suffixes)


def parse_field(field_string):
    tag, width, suffix = (field_string.split(",") + ["", ""])[:3]
    if width == "":
        width = None
    else:
        width = string.atoi(width)
    return Column(tag, width, suffix)


def to_minutes(value):
    return "%i:%02i" % (value / 60, value % 60)
