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

from misc import dir_depth


__version__ = "0.17.3"


def uniq(list):
    """make a list with all duplicate elements removed"""
    if not list: return []
    list[0] = [ list[0] ]
    return reduce(lambda A,x: x in A and A or A+[x], list)


def map_dict(func, dict):
    for key in dict.keys():
        dict[key] = func(dict[key])
    return dict


class Dir:
    pattern = r"\.(?:mp3|mpc|mp\+|m4a|ogg|flac|fla|flc)$"
    audio_file_extRE = re.compile(pattern, re.IGNORECASE)
    del pattern

    def __init__(self, path, basedir):
        self.path = path
        self.depth = dir_depth(path) - dir_depth(basedir)
        self._basedir = basedir  # this MUST NOT go into the summary
        self._children = None
        self._streams = None
        self._num_streams = None
        self._subdirs = None
        self._types = None
        self._size = None
        self._length = None
        self._lengths = None
        self._bitrate = None
        self._br_list = []
        self._brtype = None
        self._profile = None
        self._bad = None
        self._date = None
        self._artist = None
        self._artistver = None
        self._album = None
        self._albumver = None

    def __le__(self, other):
        """Compare the path relative to the respective basedir

        Only the paths are compared. Directory contents is not
        considered at all.
        """
        mine = conf.conf.options.sort_key(self.relpath)
        yours = conf.conf.options.sort_key(other.relpath)
        return mine <= yours

    def __eq__(self, other):
        """Compare the path relative to the respective basedir

        Only the paths are compared. Directory contents is not
        considered at all.
        """
        mine = conf.conf.options.sort_key(self.relpath)
        yours = conf.conf.options.sort_key(other.relpath)
        return mine == yours

    def __get_relpath(self):
        path = self.path.split(os.path.sep)
        return os.path.join(*path[-self.depth-1:])
    relpath = property(fget=lambda self: self.__get_relpath())

    def __get_name(self):
        return os.path.basename(self.path) or self.path
    name = property(fget=lambda self: self.__get_name())

    def children(self):
        if self._children: return self._children
        self._children = map(lambda x: os.path.join(self.path, x),
                             os.listdir(self.path))
        return self._children

    def streams(self):
        if self._streams: return self._streams
        self._streams = []
        self._bad = []
        self._num_streams = 0
        for child in self.audio_files():
            self._num_streams += 1
            try:
                self._streams.append(audiotype.openstream(child))
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except audiotype.SpacerError:
                continue
            except Exception, msg:
                self._bad.append(child)
        return self._streams

    def bad_streams(self):
        self.streams()
        return self._bad

    def __get_num_files(self):
        return len(self.audio_files())
    num_files = property(fget=lambda self: self.__get_num_files())

    def types(self):
        if self._types != None: return self._types
        types = map(lambda x: x.type(), self.streams())
        self._types = uniq(types)
        self._types.sort()
        return self._types

    def __get_mediatype(self):
        if not self.types():
            return "?"
        elif len(self.types()) == 1:
            return self.types()[0]
        else:
            return "Mixed"
    mediatype = property(fget=lambda self: self.__get_mediatype())

    def __get_artist(self):
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
            self._artistver = -1
            return

        if conf.conf.options.prefer_tag == 1:
            if v1taint != 1:
                self._artist = v1uniq[0]
                self._artistver = 1
            else:
                self._artist = v2uniq[0]
                self._artistver = 2
        elif conf.conf.options.prefer_tag == 2:
            if v2taint != 1:
                self._artist = v2uniq[0]
                self._artistver = 2
            else:
                self._artist = v1uniq[0]
                self._artistver = 1
        else:
            print >> sys.stderr, "Invalid argument to --prefer-tag or -P"
            sys.exit(1)

        return self._artist
    artist = property(fget=lambda self: self.__get_artist())

    def __get_album(self):
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
            self._albumver = -1
            return

        if conf.conf.options.prefer_tag == 1:
            if v1taint != 1:
                self._album = v1uniq[0]
                self._albumver = 1
            else:
                self._album = v2uniq[0]
                self._albumver = 2
        elif conf.conf.options.prefer_tag == 2:
            if v2taint != 1:
                self._album = v2uniq[0]
                self._albumver = 2
            else:
                self._album = v1uniq[0]
                self._albumver = 1
        else:
            print >> sys.stderr, "This should never happen"
            raise

        return self._album
    album = property(fget=lambda self: self.__get_album())

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
    size = property(fget=lambda self: self.get_size())

    def __get_sizes(self):
        res = dict.fromkeys(self.types(), 0)
        for mediatype in self.types():
            res[mediatype] += self.get_size(mediatype)
        return res
    sizes = property(fget=__get_sizes)

    def __get_length(self, type="all"):
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
    length = property(fget=lambda self: self.__get_length())

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

    def __get_brtype(self):
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
    brtype = property(fget=lambda self: self.__get_brtype())

    def __get_bitrate(self):
        """report average bitrate in bits per second

        If no audio is found zero is returned."""

        if self._bitrate: return self._bitrate
        if self.brtype != "C": self._variable_bitrate()
        return self._bitrate
    bitrate = property(fget=lambda self: self.__get_bitrate())

    def __get_profile(self):
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
    profile = property(fget=lambda self: self.__get_profile())

    def __get_quality(self):
        if self.profile: return self.profile
        return "%s %s" % (self.bitrate / 1000, self.brtype)
    quality = property(fget=lambda self: self.__get_quality())

    def __get_audiolist_format(self):
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
    audiolist_format = property(fget=lambda self: self.__get_audiolist_format())

    def __get_modified(self):
        if self._date: return self._date
        dates = map(lambda x: x.modified(), self.streams())
        dates.append(os.path.getmtime(self.path))
        self._date = max(dates)
        return self._date
    modified = property(fget=lambda self: self.__get_modified())

    def audio_files(self):
        """Return a list of all audio files based on file extensions"""
        return [ file for file in self.children() if self.is_audio_file(file) ]

    def cache_key(self):
        """Make a cache key for this directory"""
        files = tuple(self.audio_files())
        return (self.path, self.modified, files)

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
