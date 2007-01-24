# -*- coding: iso-8859-1 -*-
#
# A module for gathering information about a directory of audio files
#
# This program is under GPL license. See COPYING file for details.
#
# Copyright 2003,2006
# Sylvester Johansson <sylvestor@telia.com>
# Mattias Päivärinta <pejve@vasteras2.net>


import re, os, string, time
import audiotype, conf

import app
from cache import PersistentDict
from cache import memoized
from misc import dir_depth
from misc import map_dict
from misc import uniq


__version__ = "0.17.3"


DIR_PERSISTENCE_FILE = app.user_data_file('dirs.pkl')


def set_root(self, root):
    # XXX These things don't belong here!!
    self._root = root
    self._depth = dir_depth(self.path) - dir_depth(root) - 1
    path = self.path.split(os.path.sep)
    self._relpath = os.path.join(*path[-self._depth-1:])


class Dir(object):
    pattern = r"\.(?:mp3|mpc|mp\+|m4a|ogg|flac|fla|flc)$"
    audio_file_extRE = re.compile(pattern, re.IGNORECASE)
    del pattern

    def __init__(self, path):
        self._streams = None
        self._types = None
        self._size = None
        self._length = None
        self._bitrate = None
        self._brtype = None
        self._profile = None
        self._artist = None
        self._artistver = None
        self._album = None

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

        del self._streams
        del self._types
        del self._size
        del self._length
        del self._bitrate
        del self._brtype
        del self._profile
        del self._artist
        del self._album

    def get_name(self):
        return os.path.basename(self.path) or self.path

    def children(self):
        return [ os.path.join(self.path, f) for f in os.listdir(self.path) ]

    def streams(self):
        if self._streams: return self._streams
        self._streams = []
        self.bad_files = []
        for child in self.audio_files:
            try:
                self._streams.append(audiotype.openstream(child))
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except audiotype.SpacerError:
                continue
            except Exception, msg:
                self.bad_files.append(child)
        return self._streams

    def get_bad_files(self):
        self.streams()
        return self.bad_files

    def get_num_files(self):
        return len(self.audio_files)

    def types(self):
        if self._types != None: return self._types
        types = map(lambda x: x.type(), self.streams())
        self._types = uniq(types)
        self._types.sort()
        return self._types

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
                return
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
            self._artist = None
            return

        if conf.conf.options.prefer_tag == 1:
            if v1taint != 1:
                self._artist = v1uniq[0]
            else:
                self._artist = v2uniq[0]
        elif conf.conf.options.prefer_tag == 2:
            if v2taint != 1:
                self._artist = v2uniq[0]
            else:
                self._artist = v1uniq[0]
        else:
            print >> sys.stderr, "Invalid argument to --prefer-tag or -P"
            sys.exit(1)

        return self._artist

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
                return
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
            self._album = None
            return

        if conf.conf.options.prefer_tag == 1:
            if v1taint != 1:
                self._album = v1uniq[0]
            else:
                self._album = v2uniq[0]
        elif conf.conf.options.prefer_tag == 2:
            if v2taint != 1:
                self._album = v2uniq[0]
            else:
                self._album = v1uniq[0]
        else:
            print >> sys.stderr, "This should never happen"
            raise

        return self._album

    def get_size(self, type="all"):
        """report size in bytes

        Note: The size reported is the total audio file size, not the
        total directory size."""

        if self._size != None: return self._size[type]
        self._size = {}
        self._size["all"] = 0
        for file in self.streams():
            if file.type() in self._size:
                self._size[file.type()] += file.streamsize()
            else:
                self._size[file.type()] = file.streamsize()
            self._size["all"] += file.streamsize()
        return self._size[type]

    def get_sizes(self):
        res = dict.fromkeys(self.types(), 0)
        for mediatype in self.types():
            res[mediatype] += self.get_size(mediatype)
        return res

    def get_length(self, type="all"):
        if self._length != None: return self._length[type]
        tot = 0
        self._length = {}
        self._length["all"] = 0
        for file in self.streams():
            if file.type() in self._length:
                self._length[file.type()] += file.time
            else:
                self._length[file.type()] = file.time
            self._length["all"] += file.time
        self._length = map_dict(int, self._length)
        return self._length[type]

    def _variable_bitrate(self):
        if self.length == 0:
            self._bitrate = 0
        else:
            self._bitrate = int(self.size * 8.0 / self.length)

    def _constant_bitrate(self):
        for file in self.streams():
            br = file.bitrate()
            if self._bitrate == None:
                self._bitrate = br
            elif self._bitrate != br:
                self._brtype = "~"
                self._variable_bitrate()
        self._bitrate = int(self._bitrate)

    def get_brtype(self):
        """report the bitrate type

        If multiple types are found "~" is returned.
        If no audio is found the empty string is returned."""

        if self._brtype: return self._brtype
        self._brtype = ""
        if self.mediatype == "Mixed":
            self._brtype = "~"
            return self._brtype
        for file in self.streams():
            type = file.brtype()
            if self._brtype == "":
                self._brtype = type
            elif self._brtype != type:
                self._brtype = "~"
                break
        if self._brtype == "C":
            self._constant_bitrate()
        return self._brtype

    def get_bitrate(self):
        """report average bitrate in bits per second

        If no audio is found zero is returned."""

        if self._bitrate: return self._bitrate
        if self.brtype != "C": self._variable_bitrate()
        return self._bitrate

    def get_profile(self):
        if self._profile != None: return self._profile
        if self.brtype == "~":
            self._profile = ""
            return self._profile
        for file in self.streams():
            p = file.profile()
            if not self._profile:
                self._profile = p
            if not p or p != self._profile:
                self._profile = ""
                break
        return self._profile

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
        attrs = ('album artist audio_files audiolist_format bad_files bitrate '
                 'brtype length mediatype modified name num_files path profile '
                 'quality size sizes').split()
        res = {}
        for attr in attrs:
            res[attr] = getattr(self, attr)
        return res

CachedDir = memoized(Dir, PersistentDict(filename=DIR_PERSISTENCE_FILE, default={}))
