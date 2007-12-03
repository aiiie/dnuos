"""Holds metadata for directories of audio"""

import os
import re
import sys
from traceback import format_exception

try:
    set
except ImportError:
    from sets import Set as set

from dnuos import audiotype
from dnuos.misc import dir_depth


class Dir(object):
    pattern = r"\.(?:mp3|mpc|mp\+|m4a|ogg|flac|fla|flc)$"
    audio_file_extRE = re.compile(pattern, re.IGNORECASE)
    del pattern

    __slots__ = tuple('albums artists _audio_files _bad_files '
                      '_bitrates _lengths _types modified path '
                      '_profiles sizes _vendors'.split())
    __version__ = '1.0'

    def __init__(self, path):
        self.path = path
        self.modified = None
        self._audio_files = []

    def load(self):
        self._audio_files = self._parse_audio_files()
        streams, self._bad_files = self.get_streams()
        self.artists = self._parse_artist(streams)
        self.albums = self._parse_album(streams)
        self.sizes = self._parse_size(streams)
        self._lengths = self._parse_length(streams)
        self._types = self._parse_types(streams)
        self._bitrates = self._parse_bitrates(streams)
        self._profiles = self._parse_profile(streams)
        self._vendors = self._parse_vendors(streams)
        self.modified = self._parse_modified()

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
        return [f for f in os.listdir(self.path)]

    def get_streams(self):
        streams = []
        bad_files = []
        for child in self._audio_files:
            filename = os.path.join(self.path, child)
            try:
                streams.append(audiotype.openstream(filename))
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except audiotype.SpacerError:
                continue
            except Exception, msg:
                tb = ''.join(format_exception(*sys.exc_info()))
                bad_files.append((child, tb))
        return streams, bad_files

    def _get_bad_files(self):
        return [(os.path.join(self.path, f), tb) for (f, tb)
                in self._bad_files]
    bad_files = property(_get_bad_files)

    def _get_num_files(self):
        return len(self._audio_files)
    num_files = property(_get_num_files)

    def _parse_types(self, streams):
        types = list(set([s.filetype for s in streams]))
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
                res.setdefault(tag, set()).add(artist)
        return res

    def _parse_album(self, streams):
        res = {}
        for stream in streams:
            for tag, album in stream.album().items():
                res.setdefault(tag, set()).add(album)
        return res

    def _parse_size(self, streams):
        """report size in bytes

        Note: The size reported is the total audio file size, not the
        total directory size."""

        size = {}
        for file_ in streams:
            if file_.filetype in size:
                size[file_.filetype] += file_.filesize
            else:
                size[file_.filetype] = file_.filesize
        return size

    def _get_size(self):
        return sum(self.sizes.values())
    size = property(_get_size)

    def _parse_length(self, streams):
        length = {}
        for file in streams:
            if file.filetype in length:
                length[file.filetype] += file.time
            else:
                length[file.filetype] = file.time
        return length

    def _get_length(self):
        return sum(self._lengths.values())
    length = property(_get_length)

    def _parse_bitrates(self, streams):
        return tuple(set([(s.bitrate(), s.brtype)
                          for s in streams]))

    def _get_brtype(self):
        """report the bitrate type

        If multiple types are found "~" is returned.
        If no audio is found the empty string is returned."""

        if self.mediatype == "Mixed":
            return "~"
        types = tuple(set([type_ for (br, type_) in self._bitrates]))
        brs = tuple(set([br for (br, type_) in self._bitrates]))
        if len(types) < 1:
            return ""
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
            return self._bitrates[0][0]
        if self.length == 0:
            return 0
        else:
            return self.size * 8.0 / self.length
    bitrate = property(_get_bitrate)

    def _parse_profile(self, streams):
        res = {}
        for s in streams:
            for key, profile in s.profile().items():
                res.setdefault(key, set()).add(profile)
        return res

    def _get_profile(self):
        """
        report encoding profile name

        If no or inconsistent profiles are detected, an empty string
        is returned.
        """
        if len(self._profiles) == 1:
            profiles = self._profiles.values()[0]
        else:
            profiles = set()

        if len(profiles) == 1:
            return tuple(profiles)[0]
        else:
            return ""
    profile = property(_get_profile)

    def _parse_vendors(self, streams):
        return tuple(set([s.vendor for s in streams]))

    def _get_vendor(self):
        if self.mediatype == 'Mixed' or len(self._vendors) > 1:
            return 'Mixed'
        return self._vendors[0]
    vendor = property(_get_vendor)

    def _get_quality(self):
        if self.profile:
            return self.profile
        return "%i %s" % (int(self.bitrate) / 1000, self.brtype)
    quality = property(_get_quality)

    def _get_audiolist_format(self):
        table = {"V": "VBR",
                 "L": "LL"}
        res = set()
        for br, type_ in self._bitrates:
            if type_ == "C":
                res.add(br / 1000)
            else:
                res.add(table[type_])
        res = list(res)
        res.sort()
        return ', '.join([str(int(x)) for x in res])
    audiolist_format = property(_get_audiolist_format)

    def _parse_modified(self):
        files = self.audio_files[:]
        files.append(self.path)
        dates = [os.path.getmtime(f) for f in files]
        return max(dates)

    def _parse_audio_files(self):
        return [filename
                for filename in self.children()
                if self.is_audio_file(os.path.join(self.path, filename))]

    def _get_audio_files(self):
        """Return a list of all audio files based on file extensions"""
        return [os.path.join(self.path, filename)
                 for filename in self._audio_files]
    audio_files = property(_get_audio_files)

    def is_valid(self):
        try:
            valid = (self.modified == self._parse_modified() and
                     self._audio_files == self._parse_audio_files())
        except OSError:
            valid = False
        return valid

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
        return [getattr(self, attrname)
                for attrname in Dir.__slots__]

    def __setstate__(self, state):
        for key, value in zip(Dir.__slots__, state):
            setattr(self, key, value)
