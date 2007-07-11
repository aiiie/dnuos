# -*- coding: iso-8859-1 -*-
# vim: tabstop=4 expandtab shiftwidth=4
#
# A module for gathering information about a directory of audio files
#
# This program is under GPL license. See COPYING file for details.
#
# Copyright 2003,2006
# Sylvester Johansson <sylvestor@telia.com>
# Mattias Päivärinta <pejve@vasteras2.net>


import re, os, string, time
from sets import Set

import audiotype
import appdata
import dnuos.output.db
from conf import Settings
from misc import dir_depth
from misc import map_dict
from misc import uniq


__version__ = "0.17.3"


class Dir(object):
    pattern = r"\.(?:mp3|mpc|mp\+|m4a|ogg|flac|fla|flc)$"
    audio_file_extRE = re.compile(pattern, re.IGNORECASE)
    del pattern

    __slots__ = tuple('_album _artist audio_files audiolist_format bad_files '
                      'bitrate brtype length mediatype modified path profile _size'.split())

    def __init__(self, path):
        self.path = path
        self.audio_files = self.get_audio_files()
        self._artist = self._parse_artist()
        self._album = self._parse_album()
        self._size = self._parse_size()
        self.length = self.get_length()
        self.mediatype = self.get_mediatype()
        self.brtype = self.get_brtype()
        self.bitrate = self.get_bitrate()
        self.profile = self.get_profile()
        self.audiolist_format = self.get_audiolist_format()
        self.modified = self.get_modified()
        self.bad_files = self.get_bad_files()

    def textencode(self, str):
        try:
            x = unicode(str, "ascii")
        except UnicodeError:
            str = unicode(str, "latin1")
        except TypeError:
            pass
        else:
            pass

        if Settings().options.output_module == dnuos.output.db:
            encoding = ('latin1', 'replace')
        else:
            encoding = ('utf-8',)
        return str.encode(*encoding).strip('\0')

    def depth_from(self, root):
        """
        Return the relative depth of the directory from the given
        root.
        """
        return dir_depth(self.path) - dir_depth(root) - 1

    def _get_name(self):
        return os.path.basename(self.path) or self.path
    name = property(_get_name)

    def children(self):
        return [ os.path.join(self.path, f) for f in os.listdir(self.path) ]

    def streams(self):
        streams = []
        self.bad_files = []
        for child in self.audio_files:
            try:
                force_old_lame_presets = Settings().options.force_old_lame_presets
                streams.append(audiotype.openstream(child,
                                                    force_old_lame_presets))
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except audiotype.SpacerError:
                continue
            except Exception, msg:
                self.bad_files.append(child)
        return streams

    def get_bad_files(self):
        self.streams()
        return self.bad_files

    def _get_num_files(self):
        return len(self.audio_files)
    num_files = property(_get_num_files)

    def types(self):
        types = list(Set([ s.type() for s in self.streams() ]))
        types.sort()
        return types

    def get_mediatype(self):
        """Return the collective media type for the directory

        Return values:
            "?"     - The directory contains no non-broken audiofiles
            "Mixed" - The directory contains multiple kinds of audiofiles
            other   - The uniform mediatype of all non-broken audiofiles
        """
        if not self.types():
            return "?"
        elif len(self.types()) == 1:
            return self.types()[0]
        else:
            return "Mixed"

    def _parse_artist(self):
        res = {}
        for stream in self.streams():
            for tag, artist in stream.artist().items():
                res.setdefault(tag, Set()).add(artist)
        return res

    def _parse_album(self):
        res = {}
        for stream in self.streams():
            for tag, album in stream.album().items():
                res.setdefault(tag, Set()).add(album)
        return res

    def _get_artist(self):
        if len(self._artist) == 1:
            keys = self._artist.keys()
            encoder = lambda x: x
        elif Set(self._artist.keys()) == Set(['id3v1', 'id3v2']):
            if Settings().options.prefer_tag == 1:
                keys = ['id3v1', 'id3v2']
            elif Settings().options.prefer_tag == 2:
                keys = ['id3v2', 'id3v1']
            encoder = self.textencode
        else:
            return None

        for key in keys:
            values = self._artist[key]
            if len(values) != 1:
                return None
            elif values != Set([None]):
                return encoder(values.pop())
            else:
                pass
    artist = property(_get_artist)

    def _get_album(self):
        if len(self._album) == 1:
            keys = self._album.keys()
            encoder = lambda x: x
        elif Set(self._album.keys()) == Set(['id3v1', 'id3v2']):
            if Settings().options.prefer_tag == 1:
                keys = ['id3v1', 'id3v2']
            elif Settings().options.prefer_tag == 2:
                keys = ['id3v2', 'id3v1']
            encoder = self.textencode
        else:
            return None

        for key in keys:
            values = self._album[key]
            if len(values) != 1:
                return None
            elif values != Set([None]):
                return encoder(values.pop())
            else:
                pass
    album = property(_get_album)

    def _parse_size(self):
        """report size in bytes

        Note: The size reported is the total audio file size, not the
        total directory size."""

        size = {}
        for file in self.streams():
            if file.type() in size:
                size[file.type()] += file.streamsize()
            else:
                size[file.type()] = file.streamsize()
        return size

    def _get_size(self):
        return sum(self._size.values())
    size = property(_get_size)

    def _get_sizes(self):
        return self._size
    sizes = property(_get_sizes)

    def get_length(self, type="all"):
        tot = 0
        length = {}
        length["all"] = 0
        for file in self.streams():
            if file.type() in length:
                length[file.type()] += file.time
            else:
                length[file.type()] = file.time
            length["all"] += file.time
        length = map_dict(int, length)
        return length[type]

    def _variable_bitrate(self):
        if self.length == 0:
            return 0
        else:
            return int(self.size * 8.0 / self.length)

    def _constant_bitrate(self):
        bitrate = None
        for file in self.streams():
            br = file.bitrate()
            if bitrate == None:
                bitrate = br
            elif bitrate != br:
                return self._variable_bitrate(), "~"
        return int(bitrate), "C"

    def get_brtype(self):
        """report the bitrate type

        If multiple types are found "~" is returned.
        If no audio is found the empty string is returned."""

        if self.mediatype == "Mixed":
            return "~"
        brtype = ""
        for file in self.streams():
            type = file.brtype()
            if brtype == "":
                brtype = type
            elif brtype != type:
                return "~"
        if brtype == "C":
            bitrate, brtype = self._constant_bitrate()
        return brtype

    def get_bitrate(self):
        """report average bitrate in bits per second

        If no audio is found zero is returned."""

        if self.brtype == "C":
            bitrate, brtype = self._constant_bitrate()
        else:
            bitrate = self._variable_bitrate()
        return bitrate

    def get_profile(self):
        """
        report encoding profile name

        If no or inconsistent profiles are detected, an empty string
        is returned.
        """
        profiles = Set([ file.profile() for file in self.streams() ])
        if len(profiles) != 1:
          return ""
        else:
          return profiles.pop()

    def _get_quality(self):
        if self.profile: return self.profile
        return "%s %s" % (self.bitrate / 1000, self.brtype)
    quality = property(_get_quality)

    def get_audiolist_format(self):
        if self.brtype == "V": return "VBR"
        list = []
        for stream in self.streams():
            if stream.brtype() == "C":
                br = stream.bitrate() / 1000
            else:
                table = {"V": "VBR",
                     "L": "LL"}
                br = table[stream.brtype()]
            if br not in list: list.append(br)
        list.sort()
        return string.join(map(str, list), ", ")

    def get_modified(self):
        files = self.audio_files[:]
        files.append(self.path)
        dates = [ os.path.getmtime(f) for f in files ]
        return max(dates)

    def get_audio_files(self):
        """Return a list of all audio files based on file extensions"""
        return [ file for file in self.children() if self.is_audio_file(file) ]

    def validate(self):
        if (self.modified != self.get_modified() or
            self.audio_files != self.get_audio_files()):
            self.__init__(self.path)

    def is_audio_file(filename):
        """Test if a filename has the extension of an audio file

        >> Dir.is_audio_file('some.mp3')
        True
        >>> Dir.is_audio_file('some.m3u')
        False
        """
        return (os.path.isfile(filename) and
                Dir.audio_file_extRE.search(filename))
    is_audio_file = staticmethod(is_audio_file)

    def __getstate__(self):
        return [ getattr(self, attrname)
                 for attrname in Dir.__slots__]

    def __setstate__(self, state):
        for key, value in zip(Dir.__slots__, state):
            setattr(self, key, value)
