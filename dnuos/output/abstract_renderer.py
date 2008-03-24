import locale
import time
import unicodedata

try:
    set
except NameError:
    from sets import Set as set

from dnuos.misc import to_human, _

class AbstractRenderer(object):

    def setup_columns(self, fields, options):

        self.columns = [parse_field(f, options) for f in fields]


class Column(object):

    def __init__(self, tag, width, suffix, options):

        attr_table = {
            "a": (_('Bitrate(s)'), lambda adir: adir.audiolist_format),
            "A": (_('Artist'), self._get_artist),
            "b": (_('Bitrate'), lambda adir: adir.bitrate),
            "B": (_('Bitrate'), lambda adir: adir.bitrate),
            "C": (_('Album'), self._get_album),
            "f": (_('Files'), lambda adir: adir.num_files),
            "l": (_('Length'), lambda adir: adir.length),
            "L": (_('Length'), lambda adir: adir.length),
            "m": (_('Modified'), lambda adir: adir.modified),
            "M": (_('Modified'), lambda adir: adir.modified),
            "n": (_('Album/Artist'), lambda adir: adir.name),
            "N": (_('Album/Artist'), lambda adir: adir.name),
            "p": (_('Profile'), self._get_profile),
            "P": (_('Path'), lambda adir: adir.path),
            "q": (_('Quality'), lambda adir: adir.quality),
            "s": (_('Size'), lambda adir: adir.size),
            "S": (_('Size'), lambda adir: adir.size),
            "t": (_('Type'), lambda adir: adir.mediatype),
            "T": (_('BR Type'), lambda adir: adir.brtype),
            "V": (_('Encoder'), lambda adir: adir.vendor),
        }

        formatter_table = {
            "b": lambda data, depth: to_human(int(data), 1000.0),
            "B": lambda data, depth: locale.format('%d', data),
            "l": lambda data, depth: to_minutes(int(data)),
            "L": lambda data, depth: locale.format('%d', data),
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

        return str_.encode(*self._encoding).split('\0', 1)[0]

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
                if not isinstance(data, unicode):
                    data = data.decode('utf-8')
                data = unicodedata.normalize('NFC', data)
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
