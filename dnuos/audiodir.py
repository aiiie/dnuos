# -*- coding: iso-8859-1 -*-
# vim: tabstop=4 expandtab shiftwidth=4
#
# A module for gathering information about a directory of audio files
#
# This program is under GPL license. See COPYING file for details.
#
# Copyright 2003,2006
# Sylvester Johansson <sylvestor@telia.com>
# Mattias P�iv�rinta <pejve@vasteras2.net>


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

    def __init__(self, path):
        self.path = path
        self.audio_files = self.get_audio_files()
        self.name = self.get_name()
        self.num_files = self.get_num_files()
        self.mediatype = self.get_mediatype()
        self.artist = self.get_artist()
        self.album = self.get_album()
        self.size = self.get_size()
        self.sizes = self.get_sizes()
        self.length = self.get_length()
        self.brtype = self.get_brtype()
        self.bitrate = self.get_bitrate()
        self.profile = self.get_profile()
        self.quality = self.get_quality()
        self.audiolist_format = self.get_audiolist_format()
        self.modified = self.get_modified()
        self.bad_files = self.get_bad_files()

    def depth_from(self, root):
        """
        Return the relative depth of the directory from the given
        root.
        """
        return dir_depth(self.path) - dir_depth(root) - 1

    def get_name(self):
        return os.path.basename(self.path) or self.path

    def children(self):
        return [ os.path.join(self.path, f) for f in os.listdir(self.path) ]

    def streams(self):
        streams = []
        self.bad_files = []
        for child in self.audio_files:
            try:
                if Settings().options.output_module == dnuos.output.db:
                    encoding = ('latin1', 'replace')
                else:
                    encoding = ('utf-8',)
                force_old_lame_presets = Settings().options.force_old_lame_presets
                streams.append(audiotype.openstream(child,
                                                    encoding,
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

    def get_num_files(self):
        return len(self.audio_files)

    def types(self):
        types = map(lambda x: x.type(), self.streams())
        types = uniq(types)
        types.sort()
        return types

    def get_mediatype(self):
        if not self.types():
            return "?"
        elif len(self.types()) == 1:
            return self.types()[0]
        else:
            return "Mixed"

    def get_artist(self):
        if self.mediatype in ("Ogg", "AAC"):
            taint = 0
            names = map(lambda x: x.artist(), self.streams())

            if len(names) != self.num_files:
                taint = 1
            namesuniq = uniq(names)
            namesuniq.sort()

            if len(namesuniq) != 1 or namesuniq[0] == None:
                taint = 1

            if taint == 1:
                return None
            else:
                return namesuniq[0]

        v1taint = 0
        v2taint = 0
        v1 = map(lambda x: x.v1artist(), self.streams())
        v2 = map(lambda x: x.v2artist(), self.streams())

        if len(v1) != self.num_files:
            v1taint = 1
        if len(v2) != self.num_files:
            v2taint = 1

        v1uniq = uniq(v1)
        v1uniq.sort()
        v2uniq = uniq(v2)
        v2uniq.sort()

        if len(v1uniq) != 1 or v1uniq[0] == None:
            v1taint = 1
        if len(v2uniq) != 1 or v2uniq[0] == None:
            v2taint = 1

        if v1taint == 1 and v2taint == 1:
            return None

        if Settings().options.prefer_tag == 1:
            if v1taint != 1:
                return v1uniq[0]
            else:
                return v2uniq[0]
        elif Settings().options.prefer_tag == 2:
            if v2taint != 1:
                return v2uniq[0]
            else:
                return v1uniq[0]
        else:
            print >> sys.stderr, "Invalid argument to --prefer-tag or -P"
            sys.exit(1)

    def get_album(self):
        if self.mediatype in ("Ogg", "AAC"):
            taint = 0
            names = map(lambda x: x.album(), self.streams())

            if len(names) != self.num_files:
                taint = 1
            namesuniq = uniq(names)
            namesuniq.sort()

            if len(namesuniq) != 1 or namesuniq[0] == None:
                taint = 1

            if taint == 1:
                return None
            else:
                return namesuniq[0]

        v1taint = 0
        v2taint = 0
        v1 = map(lambda x: x.v1album(), self.streams())
        v2 = map(lambda x: x.v2album(), self.streams())

        if len(v1) != self.num_files:
            v1taint = 1
        if len(v2) != self.num_files:
            v2taint = 1

        v1uniq = uniq(v1)
        v1uniq.sort()
        v2uniq = uniq(v2)
        v2uniq.sort()

        if len(v1uniq) != 1 or v1uniq[0] == None:
            v1taint = 1
        if len(v2uniq) != 1 or v2uniq[0] == None:
            v2taint = 1

        if v1taint == 1 and v2taint == 1:
            return None

        if Settings().options.prefer_tag == 1:
            if v1taint != 1:
                return v1uniq[0]
            else:
                return v2uniq[0]
        elif Settings().options.prefer_tag == 2:
            if v2taint != 1:
                return v2uniq[0]
            else:
                return v1uniq[0]
        else:
            print >> sys.stderr, "This should never happen"
            raise

    def get_size(self, type="all"):
        """report size in bytes

        Note: The size reported is the total audio file size, not the
        total directory size."""

        size = {}
        size["all"] = 0
        for file in self.streams():
            if file.type() in size:
                size[file.type()] += file.streamsize()
            else:
                size[file.type()] = file.streamsize()
            size["all"] += file.streamsize()
        return size[type]

    def get_sizes(self):
        res = dict.fromkeys(self.types(), 0)
        for mediatype in self.types():
            res[mediatype] += self.get_size(mediatype)
        return res

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

    def get_quality(self):
        if self.profile: return self.profile
        return "%s %s" % (self.bitrate / 1000, self.brtype)

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
        # XXX Not sure if this attribute list is necessary now that _root,
        # _depth and _relpath are gone. Maybe we could just return
        # self.__dict__ or something.
        attrs = ('album artist audio_files audiolist_format bad_files bitrate '
                 'brtype length mediatype modified name num_files path profile '
                 'quality size sizes').split()
        res = {}
        for attr in attrs:
            res[attr] = getattr(self, attr)
        return res
