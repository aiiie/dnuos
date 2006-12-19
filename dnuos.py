#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Script gathering information about directory trees of audio files
#
# This program is under GPL license. See COPYING file for details.
#
# Copyright 2003,2006
# Sylvester Johansson <sylvestor@telia.com>
# Mattias Päivärinta <pejve@vasteras2.net>
#
# Authors
# Sylvester Johansson <sylvestor@telia.com>
# Mattias Päivärinta <pejve@vasteras2.net>



# TODO: Use list comprehension instead of bulky map and filter calls (later)
# TODO: Make specification for smoke tests (later)
# TODO: Actually create smoke tests (later)
# TODO: Consider custom character escaping (later)
# TODO: Installation guides? (later)
# TODO: [s,5] looks bad mixing 98.2 and 100M for instance (later)
# TODO: Customize metadata output? (later)
# TODO: to_human is duplicated in audiodir.py (later)


r"""Usage:  dnuos.py [options] <basedir> ...

Options:
  -b, --bitrate MIN	Exclude MP3s with bitrate lower than MIN (in Kbps)
  -B, --bg COLOR	Set HTML background color
  -D, --date		Display datestamp header
      --debug		Output debug trace to stderr
  -e, --exclude DIR	Exclude dir from search
  -f, --file FILE	Write output to FILE (cannot be used with -O /
                 	--output-db)
  -h, --help		Display this message
  -H, --html		HTML output
      --ignore-bad	Don't list files that cause Audiotype failure
  -i, --ignore-case	Case-insensitive directory sorting
  -I, --indent N	Set indent to N
  -l, --lame-only	Exclude MP3s with no LAME profile
  -L, --lame-old-preset	Report "--alt-preset xxx" for "-V x" LAME MP3s
			where applicable

  -m, --merge		Merge identical directories

			Basedirs with identical names are merged. This Means
			that all their subdirs are considered being subdirs of
			a single directory, and therefore sorted and displayed
			together. If there are duplicate names among the
			subdirs then those are also merged.

  -o, --output STRING	Set output format to STRING

			Anything enclosed by brackets is considered a field. A
			field must have the following syntax:
			  [TAG]
			  [TAG,WIDTH]
			  [TAG,WIDTH,SUFFIX]
			  [TAG,,SUFFIX]

			TAG is any of the following characters:
			  a	list of bitrates in Audiolist compatible format
			  A     artist name as found in ID3 tags
			  b	bitrate with suffix (i.e. 192k)
			  B	bitrate in bps
			  C     album name as found in ID3 tags
			  D	depth; distance from respective basedir
			  f	number of audio files (including spacers)
			  l	length in minutes and seconds
			  L	length in seconds
			  m	time of last change
			  M	time of last change in seconds since the epoch
			  n	directory name (indented)
			  N	directory name
			  p	profile
			  P	full path
			  q	quality
			  s	size with suffix (i.e. 65.4M)
			  S	size in bytes
			  t	file type
			  T	bitrate type:
				  ~	mixed files
				  C	constant bitrate
				  L	lossless compression
				  V	variable bitrate

			WIDTH defines the exact width of the field. The output
			is cropped to this width if needed. Negative values will
			give left aligned output. Cropping is always done on the
			right.

			SUFFIX lets you specify a unit to be concatenated to
			all non-empty data.

			Other interpreted sequences are:
			  \[	[
			  \]	]
			  \n	new line
			  \t	tab character

			Unescaped brackets are forbidden unless they define a
			field.

			Note: If you have any whitespace in your output string
			you must put it inside quotes or otherwise it will not
			get parsed right.

  -O, --output-db FILE	Print list in output.db format to FILE
  -P, --prefer-tag N	If both ID3v1 and ID3v2 tags exist, prefer N (1 or 2)
  -q, --quiet		Omit progress indication
  -s, --strip		Strip output of field headers and empty directories
  -S, --stats		Display statistics results
  -t, --time		Display elapsed time footer
  -T, --text COLOR	Set HTML text color
  -v, --vbr-only	Exclude MP3s with constant bitrates
  -V, --version		Display version
  -w, --wildcards	Expand wildcards in basedirs
"""


__version__ = "0.93"

import itertools
import os
import re
import string
import sys
import time

# fix for some dumb version of python 2.3
sys.path.append(os.path.abspath('.'))

import audiotype
import audiodir
import conf


class Data:
	def __init__(self):
		self.BadFiles = []
		self.Base = 0
		self.Start = 0
		self.Size = {
			"Total": 0.0,
			"FLAC": 0.0,
			"Ogg": 0.0,
			"MP3": 0.0,
			"MPC": 0.0,
			"AAC": 0.0}
		self.TimeTotal = 0.0


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


def eval_fields(fields, obj, suffixes=1):
	"""project an object through a field list into a tuple of strings"""
	list = []
	for field in fields:
		try:
			data, width, suffix = str(obj.get(field[0])), field[1], field[2]
		except KeyError:
			print >> sys.stderr, "Unknown field <%s> in format string" % field[0]
			sys.exit(1)
		if not data: suffix = " " * len(suffix)
		if suffixes: data += suffix
		if width != None: data = "%*.*s" % (width, abs(width), data)
		list.append(data)
	return tuple(list)


def main():
	if conf.conf.DispHelp:
		print >> sys.stderr, __doc__
		return 0
	if conf.conf.OutputFormat == "HTML":
		htmlheader()
	if conf.conf.Folders:
		keys = conf.conf.Folders.keys()
		conf.conf.sort(keys)
		bases = [ conf.conf.Folders[k] for k in keys ]
		trees = [ walk(base) for base in bases ]
		dirs = itertools.chain(*trees)

		dirs = timer_wrapper(dirs)
		dirs = indicate_progress(dirs)
		if not conf.conf.OutputDb:
			dirs = collect_bad(dirs)
		dirs = filter_dirs(dirs)
		if not conf.conf.OutputDb:
			dirs = total_sizes(dirs)

		grab(dirs)

	if globals.BadFiles and not conf.conf.OutputDb:
		print ""
		print "Audiotype failed on the following files:"
		print string.join(globals.BadFiles, "\n")

	if conf.conf.DispTime:
		print ""
		print "Generation time:     %8.2f s" % globals.ElapsedTime
	if conf.conf.DispResult and not conf.conf.OutputDb:
		statistics = [
			["Ogg", globals.Size["Ogg"]],
			["MP3", globals.Size["MP3"]],
			["MPC", globals.Size["MPC"]],
			["AAC", globals.Size["AAC"]],
			["FLAC", globals.Size["FLAC"]]]
		line = "+-----------------------+-----------+"

		print ""
		print line
   		print "| Format    Amount (Mb) | Ratio (%) |"
		print line
		for x in statistics:
			if x[1]:
				print "| %-8s %12.2f | %9.2f |" % (
					x[0],
					x[1] / (1024 * 1024),
					x[1] * 100 / globals.Size["Total"])
		print line
		totalMegs = globals.Size["Total"] / (1024 * 1024)
		print "| Total %10.2f Mb   |" % totalMegs
		print "| Speed %10.2f Mb/s |" % (totalMegs / globals.ElapsedTime)
		print line[:25]
	if conf.conf.DispVersion:
		print ""
		print "dnuos version:    ", __version__
		print "audiotype version:", audiotype.__version__
	if conf.conf.OutputFormat == "HTML":
		htmlfooter()


def htmlheader():
	"""output HTML header"""
	# XXX Should we _always_ use this charset?
	print """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<title>Music List</title>
<!-- Generated by dnuos %s -->
<!-- http://dackz.net/projects/dnuos -->
<style type="text/css"><!--
body { color: %s; background: %s; }" 
-->
</style>
</head>
<body>
<pre>""" % (__version__, conf.conf.TextColor, conf.conf.BGColor)


def htmlfooter():
	"""output HTML footer"""
	print"</pre>"
	#print "<p><a href=\"http://validator.w3.org/check/referer\">"
	#print "<img src=\"http://www.w3.org/Icons/valid-html401\" alt=\"Valid HTML 4.01!\" height=\"31\" width=\"88\"></a></p>"
	print"</body></html>"


def headers(token):
	if token == "header" and not conf.conf.Stripped:  #top header
		line = conf.conf.OutputString % eval_fields(conf.conf.Fields, HeaderObject(), 0)
		print line
		print "=" * len(line)
	elif token == "date":  #date
		print time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())


def debug(msg):
	"""print debug message"""
	if conf.conf.Debug: print >> sys.stderr, "?? " + msg


class HeaderObject:
	def __init__(self):
		pass

	def get(self, id):
		dict = {
			"a": "Bitrate(s)",
			"A": "Artist",
			"b": "Bitrate",
			"B": "Bitrate",
			"c": "Channels",
			"C": "Album",
			"d": "Dir",
			"D": "Depth",
			"f": "Files",
			"l": "Length",
			"L": "Length",
			"m": "Modified",
			"n": "Album/Artist",
			"N": "Album/Artist",
			"p": "Profile",
			"P": "Path",
			"q": "Quality",
			"r": "Sample Rate",
			"s": "Size",
			"S": "Size",
			"t": "Type",
			"T": "BR Type"
			#"v": "Vendor",
			#"V": "Version",
			}
		return dict[id]


def indicate_progress(dirs, outs=sys.stderr):
	"""Indicate progress.

	Yields an unchanged iteration of dirs with an added side effect.
	Total size in globals.Size is updated to stderr every step
	throughout the iteration.
	"""
	for dir in dirs:
		print >> outs, "%sb processed\r" % to_human(globals.Size["Total"]),
		yield dir
	print >> outs, "\r               \r",


def collect_bad(dirs):
	"""Collect bad files.

	Yields an unchanged iteration of dirs with an added side effect.
	After each directory is yielded its bad files are taken care of.
	Bad files are appended to globals.Badfiles or output to stderr
	depending on conf.conf.Debug.
	"""
	for dir in dirs:
		yield dir

		if conf.conf.Debug:
			for badfile in dir.bad_streams():
				print >> sys.stderr, "Audiotype failed for:", badfile
		elif conf.conf.ListBad:
			globals.BadFiles += dir.bad_streams()


def filter_dirs(dirs):
	"""Filter directories according to configuration.

	Directories with no recognized files are always omitted.
	Directories can also be omitted as per -bvL settings.
	"""
	for dir in dirs:
		if not dir.streams():
			continue
		if hasattr(dir, "type") and dir.type() == "MP3":
			if conf.conf.NoCBR == 1 and (dir.brtype() == "~" or dir.brtype() == "C"):
				continue
			if conf.conf.NoNonProfile == 1 and dir.profile() == "":
				continue
			if dir.bitrate() < conf.conf.MP3MinBitRate:
				continue
			if conf.conf.OutputDb and \
			   (dir.type() == "Mixed" or \
			    dir.get('A') == None or \
			    dir.get('C') == None):
				continue

		yield dir


def total_sizes(dirs):
	"""Calculate audio file size totals.

	Yields an unchanged iteration of dirs with an added side effect.
	After each directory is yielded its filesize statistics are
	added to globals.Size.
	"""
	for dir in dirs:
		yield dir
		for type in dir.types():
			globals.Size[type] += dir.size(type)
		globals.Size["Total"] += dir.size()


def timer_wrapper(dirs):
    """Time the iteration.

    Yields an unchanged iteration of dirs with an added side effect.
    Time in seconds elapsed over the iteration is stored in
    globals.ElapsedTime.
    """
    globals.Start = time.clock()
    for dir in dirs:
        yield dir
    globals.ElapsedTime = time.clock() - globals.Start


class EmptyDir:
    """
    Represent a group of merged empty directories.
    """
    def __init__(self, name, depth):
        self.name = name
        self.depth = depth

    def get(self, id):
        if id == "n":
            return ' ' * conf.conf.Indent * self.depth + self.name
        else:
            return ""


def grab(dirs):
    if not conf.conf.OutputDb:
        for dir in dirs:
            outputplain(dir)
    else:
        outputdb(dirs)


oldpath = []
def outputplain(dir):
	"""Render a directory to stdout.

	Directories are rendered according to the -o settings. Ancestral
	directories are rendered as empty unless they were previously
	rendered. Pre-order directory tree traversal is assumed.
	"""
	global oldpath

    if conf.conf.DispDate:
        headers("date")
    headers("header")

	# delayed output
	path = dir.path.split(os.path.sep)[-dir.depth-1:]
	i = 0
	while i < min(len(path) - 1, len(oldpath)) and path[i] == oldpath[i]: i += 1
	while i < len(path) - 1:
		fields = eval_fields(conf.conf.Fields, EmptyDir(path[i], i))
		print conf.conf.OutputString % fields
		i += 1
	oldpath = path

	fields = eval_fields(conf.conf.Fields, dir)
	print conf.conf.OutputString % fields


def outputhtml(dirs):
    """Render directories as HTML to stdout.

    Directories are rendered like in plain text, but with HTML header
    and footer.
    """
    # XXX Should we _always_ use this charset?
    print """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<title>Music List</title>
<!-- Generated by dnuos %s -->
<!-- http://dackz.net/projects/dnuos -->
<style type="text/css"><!--
body { color: %s; background: %s; }
-->
</style>
</head>
<body>
<pre>""" % (__version__, conf.conf.TextColor, conf.conf.BGColor)

    outputplain(dirs)

    print"</pre>"
    #print "<p><a href=\"http://validator.w3.org/check/referer\">"
    #print "<img src=\"http://www.w3.org/Icons/valid-html401\" alt=\"Valid HTML 4.01!\" height=\"31\" width=\"88\"></a></p>"
    print"</body></html>"


def outputdb(dirs):
    for dir in dirs:
        print "%d:'%s',%d:'%s',%d:'%s',%d:'%s',%d,%.d,%d" % (
            len(str(dir.get('A'))),
            str(dir.get('A')),
            len(str(dir.get('C'))),
            str(dir.get('C')),
            len(str(dir.get('t'))),
            str(dir.get('t')),
            len(str(dir.get('p'))),
            str(dir.get('p')),
            dir.get('f'),
            dir.get('B') / 1000,
            dir.get('L')
        )


def subdirectories(dirs):
	dirdict = {}
	for dir in dirs:
		for path in dir.subdirs():
			key = os.path.basename(path)
			if dirdict.has_key(key):
				dirdict[key].append(path)
			else:
				dirdict[key] = [ path ]
	return dirdict


def walk(pathlist, depth=0):
	"""Traverse one or more merged directory trees in parallell in pre order.

	The subdirectories of all pathlist directories are considered
	together. They are traversed in lexicographical order by basename.
	If subdirectories of two or more pathlist directories share the same
	basename, those subdirectories are traversed together.
	"""
	# create Dir objects for all paths
	dirs = map(lambda x: audiodir.Dir(x, depth), pathlist)

	# enumerate dirs
	for dir in dirs:
		yield dir

	# create a common dictionary over the subdirectories of all Dirs
	subdir_dict = subdirectories(dirs)

	# sort keys and traverse the dictionary
	keys = subdir_dict.keys()
	conf.conf.sort(keys)
	for key in keys:
		# weed out base and excluded directories
		dirs = filter(lambda x: x not in conf.conf.ExcludePaths, subdir_dict[key])

		# recurse
		for dir in walk(dirs, depth + 1):
			yield dir


if __name__ == "__main__":
	globals = Data()
	conf.init()
	try:
		main()
	except KeyboardInterrupt:
		print >> sys.stderr, "Aborted by user"
		sys.exit(1)
