import time
import unicodedata

import dnuos.output
from dnuos.misc import to_human

class AbstractRenderer(object):

    def setup_columns(self, fields, options):

        self.columns = [parse_field(f, options) for f in fields]


class Column(object):

    def __init__(self, tag, width, suffix, options):

        attr_table = {
            "a": ('Bitrate(s)', lambda adir: adir.audiolist_format),
            "A": ('Artist', self._get_artist),
            "b": ('Bitrate', lambda adir: adir.bitrate),
            "B": ('Bitrate', lambda adir: adir.bitrate),
            "C": ('Album', self._get_album),
            #"d": "Dir",
            #"D": ('Depth', lambda adir: adir.depth),
            "f": ('Files', lambda adir: adir.num_files),
            "l": ('Length', lambda adir: adir.length),
            "L": ('Length', lambda adir: adir.length),
            "m": ('Modified', lambda adir: adir.modified),
            "M": ('Modified', lambda adir: adir.modified),
            "n": ('Album/Artist', lambda adir: adir.name),
            "N": ('Album/Artist', lambda adir: adir.name),
            "p": ('Profile', self._get_profile),
            "P": ('Path', lambda adir: adir.path),
            "q": ('Quality', lambda adir: adir.quality),
            "s": ('Size', lambda adir: adir.size),
            "S": ('Size', lambda adir: adir.size),
            "t": ('Type', lambda adir: adir.mediatype),
            "T": ('BR Type', lambda adir: adir.brtype),
            "V": ('Encoder', lambda adir: adir.vendor),
        }

        formatter_table = {
            "b": lambda data, depth: to_human(int(data), 1000.0),
            "B": lambda data, depth: int(data),
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
            self.formatter = lambda x, y: x
        self.name, self.get = attr_table[tag]

        if options.output_module == dnuos.output.db:
            self._encoding = ('latin1', 'replace')
        else:
            self._encoding = ('utf-8',)
        self._prefer_tag = options.prefer_tag

    def _textencode(self, str_):
        try:
            unicode(str_, "ascii")
        except UnicodeError:
            str_ = unicode(str_, "latin1")
        except TypeError:
            pass
        else:
            pass

        return str_.encode(*self._encoding).strip('\0')

    def _get_tag_keys(self, data):
        if len(data) == 1:
            keys = data.keys()
            encoder = lambda x: x
        elif set(data.keys()) == set(['id3v1', 'id3v2']):
            if self._prefer_tag == 1:
                keys = ['id3v1', 'id3v2']
            elif self._prefer_tag == 2:
                keys = ['id3v2', 'id3v1']
            encoder = self._textencode
        else:
            keys = []
            encoder = lambda x: x
        return keys, encoder

    def _get_tag_value(self, data, keys):
        for key in keys:
            values = data[key]
            if len(values) != 1:
                return None
            elif values != set([None]):
                return tuple(values)[0]
            else:
                pass
        return None

    def _get_artist(self, adir):
        data = adir.artists
        if data is not None:
            keys, encoder = self._get_tag_keys(data)
            value = self._get_tag_value(data, keys)
            if value is not None:
                return encoder(value)
        return None

    def _get_album(self, adir):
        data = adir.albums
        if data is not None:
            keys, encoder = self._get_tag_keys(data)
            value = self._get_tag_value(data, keys)
            if value is not None:
                return encoder(value)
        return None

    def _get_profile(self, adir):
        return adir.profile

    def _format(self, data, suffixes):

        if suffixes:
            if data:
                data += self.suffix
            else:
                data = ' ' * len(self.suffix)
        if self.width != None:
            try:
                data = unicodedata.normalize('NFC', data.decode('utf-8'))
                data = u"%*.*s" % (self.width, abs(self.width), data)
                data = data.encode('utf-8')
            except UnicodeError:
                data = "%*.*s" % (self.width, abs(self.width), data)
        return data

    def header(self, suffixes=True):

        return self._format(self.name, suffixes)

    def get_formatted(self, adir, root, suffixes=True):

        data = self.get(adir)
        if data is None:
            data = ''
        else:
            data = str(self.formatter(data, adir.depth_from(root)))
        return self._format(data, suffixes)


def parse_field(field_string, options):

    tag, width, suffix = (field_string.split(",") + ["", ""])[:3]
    if width == "":
        width = None
    else:
        width = int(width)
    column = Column(tag, width, suffix, options)
    column.indent = (lambda basename, depth, indent=options.indent:
                     " " * indent * depth + basename)
    return column


def to_minutes(value):

    return "%i:%02i" % (value / 60, value % 60)
