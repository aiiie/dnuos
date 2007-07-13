# -*- coding: iso-8859-1 -*-
# vim: tabstop=4 expandtab shiftwidth=4
#
# A module for gathering information about a directory of audio files
#
# This program is under GPL license. See COPYING file for details.
#
# Copyright 2003,2006,2007
# Sylvester Johansson <sylvestor@telia.com>
# Mattias Päivärinta <pejve@vasteras2.net>


import os
import re
import string
from sets import Set

import audiotype
import dnuos.output.db
from conf import Settings
from misc import dir_depth


__version__ = "0.17.3"


class Dir(object):
    pattern = r"\.(?:mp3|mpc|mp\+|m4a|ogg|flac|fla|flc)$"
    audio_file_extRE = re.compile(pattern, re.IGNORECASE)
    del pattern

    __slots__ = tuple('_album _artist _audio_files _bad_files '
                      '_bitrates _lengths _types modified path '
                      '_profiles _sizes'.split())

    def __init__(self, path):
        self.path = path
        self._audio_files = self._parse_audio_files()
        streams, self._bad_files = self.get_streams()
        self._artist = self._parse_artist(streams)
        self._album = self._parse_album(streams)
        self._sizes = self._parse_size(streams)
        self._lengths = self._parse_length(streams)
        self._types = self._parse_types(streams)
        self._bitrates = self._parse_bitrates(streams)
        self._profiles = self._parse_profile(streams)
        self.modified = self._parse_modified()

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
        return [ filename for filename in os.listdir(self.path) ]

    def get_streams(self):
        streams = []
        bad_files = []
        for child in self._audio_files:
            try:
                streams.append(audiotype.openstream(os.path.join(self.path, child)))
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except audiotype.SpacerError:
                continue
            except Exception, msg:
                bad_files.append(child)
        return streams, bad_files

    def _get_bad_files(self):
        return [ os.path.join(self.path, filename) for filename in self._bad_files ]
    bad_files = property(_get_bad_files)

    def _get_num_files(self):
        return len(self._audio_files)
    num_files = property(_get_num_files)

    def _parse_types(self, streams):
        types = list(Set([ s.type() for s in streams ]))
        types.sort()
        return types

    def _get_mediatype(self):
        """Return the collective media type for the directory

        Return values:
            "?"     - The directory contains no non-broken audiofiles
            "Mixed" - The directory contains multiple kinds of audiofiles
            other   - The uniform mediatype of all non-broken audiofiles
        """
        if not self._types:
            return "?"
        elif len(self._types) == 1:
            return self._types[0]
        else:
            return "Mixed"
    mediatype = property(_get_mediatype)

    def _parse_artist(self, streams):
        res = {}
        for stream in streams:
            for tag, artist in stream.artist().items():
                res.setdefault(tag, Set()).add(artist)
        return res

    def _parse_album(self, streams):
        res = {}
        for stream in streams:
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

    def _parse_size(self, streams):
        """report size in bytes

        Note: The size reported is the total audio file size, not the
        total directory size."""

        size = {}
        for file in streams:
            if file.type() in size:
                size[file.type()] += file.streamsize()
            else:
                size[file.type()] = file.streamsize()
        return size

    def _get_size(self):
        return sum(self._sizes.values())
    size = property(_get_size)

    def _get_sizes(self):
        return self._sizes
    sizes = property(_get_sizes)

    def _parse_length(self, streams):
        length = {}
        for file in streams:
            if file.type() in length:
                length[file.type()] += file.length()
            else:
                length[file.type()] = file.length()
        return length

    def _get_length(self):
        return sum(self._lengths.values())
    length = property(_get_length)

    def _parse_bitrates(self, streams):
        return tuple(Set([ (s.bitrate(), s.brtype())
                           for s in streams ]))

    def _get_brtype(self):
        """report the bitrate type

        If multiple types are found "~" is returned.
        If no audio is found the empty string is returned."""

        if self.mediatype == "Mixed":
            return "~"
        types = tuple(Set([ type for br, type in self._bitrates ]))
        brs = tuple(Set([ br for br, type in self._bitrates ]))
        if len(types) < 1:
            return ""
        elif len(types) > 1:
            return "~"
        elif len(types) > 1:
            return "~"
        elif types[0] == "C" and len(brs) > 1:
            return "~"
        else:
            return types[0]
    brtype = property(_get_brtype)

    def _get_bitrate(self):
        """report average bitrate in bits per second

        If no audio is found zero is returned."""

        if len(self._bitrates) == 1 and self.brtype == "C":
            return int(self._bitrates[0][0])
        if self.length == 0:
            return 0
        else:
            return int(self.size * 8.0 / self.length)
    bitrate = property(_get_bitrate)

    def _parse_profile(self, streams):
        def aux(stream):
            new = stream.profile()
            old = (stream.type() == 'MP3') and stream.old_lame_preset() or None
            return (new, old)
        return tuple(Set(map(aux, streams)))

    def _get_profile(self):
        """
        report encoding profile name

        If no or inconsistent profiles are detected, an empty string
        is returned.
        """
        if Settings().options.force_old_lame_presets:
            profiles = Set([ (old or new) for new, old in self._profiles ])
        else:
            profiles = Set([ new          for new, old in self._profiles ])

        if len(profiles) == 1:
            return profiles.pop()
        else:
            return ""
    profile = property(_get_profile)

    def _get_quality(self):
        if self.profile: return self.profile
        return "%s %s" % (self.bitrate / 1000, self.brtype)
    quality = property(_get_quality)

    def _get_audiolist_format(self):
        table = {"V": "VBR",
                 "L": "LL"}
        res = Set()
        for br, type in self._bitrates:
            if type == "C":
                res.add(br / 1000)
            else:
                res.add(table[type])
        res = list(res)
        res.sort()
        return string.join([ str(x) for x in res ], ", ")
    audiolist_format = property(_get_audiolist_format)

    def _parse_modified(self):
        files = self.audio_files[:]
        files.append(self.path)
        dates = [ os.path.getmtime(f) for f in files ]
        return max(dates)

    def _parse_audio_files(self):
        return [ filename for filename in self.children() if self.is_audio_file(os.path.join(self.path, filename)) ]

    def _get_audio_files(self):
        """Return a list of all audio files based on file extensions"""
        return [ os.path.join(self.path, filename) for filename in self._audio_files ]
    audio_files = property(_get_audio_files)

    def validate(self):
        if (self.modified != self._parse_modified() or
            self._audio_files != self._parse_audio_files()):
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
