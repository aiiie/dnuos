"""output.db renderer.

output.db can be easily parsed by other programs to populate databases.

Example outout:

    4:'Beck',9:'Mutations',3:'MP3',4:'-aps',13,197,3145
    4:'Beck',7:'Odelay!',3:'MP3',4:'-aps',13,198,3254
    4:'Beck',10:'Sea Change',3:'MP3',4:'-aps',12,189,3145
    4:'Beck',15:'The Information',3:'MP3',4:'-aps',15,196,3695
"""

from dnuos.output.abstract_renderer import AbstractRenderer, Column

class DBColumn(Column):

    def __init__(self, *args, **kwargs):

        super(DBColumn, self).__init__(*args, **kwargs)
        self._encoding = ('latin1', 'replace')

class Renderer(AbstractRenderer):

    def render(self, dir_pairs, options, data):

        artist_column = DBColumn("A", None, None, options)
        album_column = DBColumn("C", None, None, options)

        for adir, root in dir_pairs:
            artist = _db_string(artist_column.get(adir))
            album = _db_string(album_column.get(adir))
            mediatype = _db_string(adir.mediatype)
            profile = _db_string(adir.profile)
            num_files = adir.num_files
            bitrate = adir.bitrate / 1000
            length = int(adir.length)
            yield "%s,%s,%s,%s,%d,%.d,%d" % (
                artist,
                album,
                mediatype,
                profile,
                num_files,
                bitrate,
                length
            )


def _db_string(data):

    if data is None:
        return "0:''"
    else:
        data = str(data)
        return "%d:'%s'" % (len(data), data)
