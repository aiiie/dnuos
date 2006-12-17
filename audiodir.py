# -*- coding: iso-8859-1 -*-
#
# A module for gathering information about a directory of audio files
#
# This program is under GPL license. See COPYING file for details.
#
# Copyright 2003  Sylvester Johansson  (sylvestor@telia.com)
#                 Mattias Päivärinta   (mpa99001@student.mdh.se)


import re, os, string, time
import audiotype, conf


__version__ = "0.17.3"


def _is_audio_file(file):
	return os.path.isfile(file) and re.search("(?i)\.(?:mp3|m4a|mp\+|mpc|ogg|flac|fla|flc)$", file)


def uniq(list):
	"""make a list with all duplicate elements removed"""
	list[0] = [ list[0] ]
	return reduce(lambda A,x: x in A and A or A+[x], list)


def map_dict(func, dict):
	for key in dict.keys():
		dict[key] = func(dict[key])
	return dict


def dir_test(dir):
	"""check if it's a readable directory"""
	if not os.path.isdir(dir) or not os.access(dir, os.R_OK):
		return 0

	# does os.access(file, os.R_OK) not work for windows?
	try:
		os.chdir(dir)
		return 1
	except OSError:
		return 0


def to_minutes(value):
	return "%i:%02i" % (value / 60, value % 60)


def to_human(value, radix=1024.0):
	i = 0
	while value >= radix:
		value /= radix
		i += 1
	suffix = " kMG"[i]
	if value > 100:
		return "%d%s" % (value, suffix)
	elif value < 10:
		return "%.2f%s" % (value, suffix)
	else:
		return "%.1f%s" % (value, suffix)


class Dir:
	def __init__(self, filename, depth=0):
		self.path = filename
		self.depth = depth
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

	def name(self):
		return os.path.basename(self.path) or self.path

	def path(self):
		return os.path.dirname(self.path)

	def children(self):
		if self._children: return self._children
		self._children = map(lambda x: os.path.join(self.path, x),
		                     os.listdir(self.path))
		return self._children

	def subdirs(self):
		if self._subdirs != None: return self._subdirs
		self._subdirs = filter(dir_test, self.children())
		return self._subdirs

	def streams(self):
		if self._streams: return self._streams
		self._streams = []
		self._bad = []
		self._num_streams = 0
		list = filter(_is_audio_file, self.children())
		for child in list:
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

	def num_files(self):
		return len(filter(_is_audio_file, self.children()))

	def types(self):
		if self._types != None: return self._types
		types = map(lambda x: x.type(), self.streams())
		self._types = uniq(types)
		self._types.sort()
		return self._types

	def type(self):
		if not self.types():
			return "?"
		elif len(self.types()) == 1:
			return self.types()[0]
		else:
			return "Mixed"

	def artist(self):
		if self.type() in ("Ogg", "AAC"):
			taint = 0
			names = map(lambda x: x.artist(), self.streams())

			if len(names) != self.num_files():
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

		if len(v1) != self.num_files():
			v1taint = 1
		if len(v2) != self.num_files():
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

		if conf.conf.PreferTag == 1:
			if v1taint != 1:
				self._artist = v1uniq[0]
				self._artistver = 1
			else:
				self._artist = v2uniq[0]
				self._artistver = 2
		elif conf.conf.PreferTag == 2:
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

	def album(self):
		if self.type() in ("Ogg", "AAC"):
			taint = 0
			names = map(lambda x: x.album(), self.streams())

			if len(names) != self.num_files():
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

		if len(v1) != self.num_files():
			v1taint = 1
		if len(v2) != self.num_files():
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

		if conf.conf.PreferTag == 1:
			if v1taint != 1:
				self._album = v1uniq[0]
				self._albumver = 1
			else:
				self._album = v2uniq[0]
				self._albumver = 2
		elif conf.conf.PreferTag == 2:
			if v2taint != 1:
				self._album = v2uniq[0]
				self._albumver = 2
			else:
				self._album = v1uniq[0]
				self._albumver = 1
		else:
			print >> sys.stderr, "Invalid argument to --prefer-tag or -P"
			sys.exit(1)

		return self._album

	def size(self, type="all"):
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

	def length(self, type="all"):
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
		if self.length() == 0:
			self._bitrate = 0
		else:
			self._bitrate = int(self.size() * 8.0 / self.length())

	def _constant_bitrate(self):
		for file in self.streams():
			br = file.bitrate()
			if self._bitrate == None:
				self._bitrate = br
			elif self._bitrate != br:
				self._brtype = "~"
				self._variable_bitrate()
		self._bitrate = int(self._bitrate)

	def brtype(self):
		"""report the bitrate type

		If multiple types are found "~" is returned.
		If no audio is found the empty string is returned."""

		if self._brtype: return self._brtype
		self._brtype = ""
		if self.type() == "Mixed":
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

	def bitrate(self):
		"""report average bitrate in bits per second

		If no audio is found zero is returned."""

		if self._bitrate: return self._bitrate
		if self.brtype() != "C": self._variable_bitrate()
		return self._bitrate

	def profile(self):
		if self._profile != None: return self._profile
		if self.brtype() == "~":
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

	def quality(self):
		if self.profile(): return self.profile()
		return "%s %s" % (self.bitrate() / 1000, self.brtype())

	def audiolist_format(self):
		if self.brtype() == "V": return "VBR"
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

	def modified(self):
		if self._date: return self._date
		dates = map(lambda x: x.modified(), self.streams())
		dates.append(os.path.getmtime(self.path))
		self._date = max(dates)
		return self._date

	def get(self, id):
		table = {
		"a": lambda: self.audiolist_format(),
		"A": lambda: self.artist(),
		"b": lambda: to_human(self.bitrate(), 1000.0),
		"B": lambda: self.bitrate(),
		"C": lambda: self.album(),
		"D": lambda: self.depth,
		"f": lambda: self.num_files(),
		"l": lambda: to_minutes(self.length()),
		"L": lambda: self.length(),
		"m": lambda: time.ctime(self.modified()),
		"M": lambda: self.modified(),
		"n": lambda: " " * conf.conf.Indent * self.depth + self.name(),
		"N": lambda: self.name(),
		"p": lambda: self.profile(),
		"P": lambda: self.path,
		"q": lambda: self.quality(),
		"s": lambda: to_human(self.size()),
		"S": lambda: self.size(),
		"t": lambda: self.type(),
		"T": lambda: self.brtype()
		}
		return table[id]()
