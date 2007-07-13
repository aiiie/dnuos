import string
from dnuos.misc import to_human


class AbstractRenderer(object):
    def setup_columns(self, fields, indent):
        self.columns = map(lambda x: parse_field(x, indent), fields)


class Column(object):
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
        formatter_table = {
            "b": lambda data, depth: to_human(data, 1000.0),
            "l": lambda data, depth: to_minutes(int(data)),
            "L": lambda data, depth: int(data),
            "m": lambda data, depth: time.ctime(data),
            "n": lambda data, depth: self.indent(data, depth),
            "s": lambda data, depth: to_human(data),
        }
        self.width, self.suffix = width, suffix
        if tag in formatter_table:
            self.formatter = formatter_table[tag]
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


def parse_field(field_string, indent):
    tag, width, suffix = (field_string.split(",") + ["", ""])[:3]
    if width == "":
        width = None
    else:
        width = string.atoi(width)
    column = Column(tag, width, suffix)
    column.indent = lambda basename, depth, indent=indent: " " * indent * depth + basename
    return column


def to_minutes(value):
    return "%i:%02i" % (value / 60, value % 60)
