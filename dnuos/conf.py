# -*- coding: iso-8859-1 -*-
#
# This program is under GPL license. See COPYING file for details.
#
# Copyright 2003,2006,2007
# Sylvester Johansson <sylvestor@telia.com>
# Mattias Päivärinta <pejve@vasteras2.net>
#
# Authors
# Sylvester Johansson <sylvestor@telia.com>
# Mattias Päivärinta <pejve@vasteras2.net>


"""
Configuration module for Dnuos.
"""


__version__ = "0.92"


import glob
from optparse import OptionParser, Option
import os
import re
import string
import sys
import time

from misc import die
from misc import dir_test


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


def to_minutes(value):
    return "%i:%02i" % (value / 60, value % 60)


class Settings:
    def __init__(self):
        self.Folders = []
        self.OutStream = sys.__stdout__
        self.Fields = []
        self.OutputString = ""

    def parse_args(self, argv=sys.argv[1:]):
        usage = "%prog [options] basedir ..."
        parser = OptionParser(usage)
        parser.set_defaults(mp3_min_bit_rate=None,
                            bg_color="white",
                            ignore_case=False,
                            indent=4,
                            debug=False,
                            disp_version=False,
                            disp_time=False,
                            disp_date=False,
                            disp_result=False,
                            exclude_paths=[],
                            list_bad=True,
                            merge=False,
                            no_cbr=False,
                            no_non_profile=False,
                            output_format="plain",
                            prefer_tag=2,
                            quiet=False,
                            raw_output_string="[n,-52]| [s,5] | [t,-4] | [q]",
                            stripped=False,
                            text_color="black",
                            wildcards=False)

        parser.add_option("-b", "--bitrate",
                          dest="mp3_min_bitrate", type="int",
                          help="Exclude MP3s with bitrate lower than MIN (in Kbps)", metavar="MIN")
        parser.add_option("-B", "--bg",
                          dest="bg_color",
                          help="Set HTML background COLOR (default %default)", metavar="COLOR")
        parser.add_option("-D", "--date",
                          dest="disp_date", action="store_true",
                          help="Display datestamp header")
        parser.add_option("--debug",
                          dest="debug", action="store_true",
                          help="Output debug trace to stderr")
        parser.add_option("-e", "--exclude",
                          dest="exclude_paths", action="append",
                          help="Exclude DIR from search", metavar="DIR")
        parser.add_option("-f", "--file",
                          dest="outfile",
                          help="Write output to FILE", metavar="FILE")
        parser.add_option("-H", "--html",
                          dest="output_format", action="store_const", const="html",
                          help="HTML output")
        parser.add_option("--ignore-bad",
                          dest="list_bad", action="store_false",
                          help="Don't list files that cause Audiotype failure")
        parser.add_option("-i", "--ignore-case",
                          dest="ignore_case", action="store_true",
                          help="Case-insensitive directory sorting")
        parser.add_option("-I", "--indent",
                          dest="indent", type="int",
                          help="Set indent to n (default %default)", metavar="n")
        parser.add_option("-l", "--lame-only",
                          dest="no_non_profile", action="store_true",
                          help="Exclude MP3s with no LAME profile")
        parser.add_option("-L", "--lame-old-preset",
                          dest="force_old_lame_presets", action="store_true",
                          help='Report "--alt-preset xxx" for "-V x" LAME MP3s where applicable')
        parser.add_option("-m", "--merge",
                          dest="merge", action="store_true",
                          help="Parse basedirs in parallell as opposed to one after the other")
        parser.add_option("-o", "--output",
                          dest="raw_output_string",
                          help="Set output format STRING used in plain-text and HTML output. Refer to documentation for details on syntax. (default %default)", metavar="STRING")
        parser.add_option("-O", "--output-db",
                          dest="output_format", action="store_const", const="db",
                          help="Print list in output.db format")
        parser.add_option("-P", "--prefer-tag",
                          dest="prefer_tag", type="int",
                          help="If both ID3v1 and ID3v2 tags exist, prefer n (1 or 2) (default %default)", metavar="n")
        parser.add_option("-q", "--quiet",
                          dest="quiet", action="store_true",
                          help="Omit progress indication")
        parser.add_option("-s", "--strip",
                          dest="stripped", action="store_true",
                          help="Strip output of field headers and empty directories")
        parser.add_option("-S", "--stats",
                          dest="disp_result", action="store_true",
                          help="Display statistics results")
        parser.add_option("-t", "--time",
                          dest="disp_time", action="store_true",
                          help="Display elapsed time footer")
        parser.add_option("-T", "--text",
                          dest="text_color",
                          help="Set HTML text COLOR (default %default)", metavar="COLOR")
        parser.add_option("-v", "--vbr-only",
                          dest="no_cbr", action="store_true",
                          help="Exclude MP3s with constant bitrates")
        parser.add_option("-V", "--version",
                          dest="disp_version", action="store_true",
                          help="Display version")
        parser.add_option("-w", "--wildcards",
                          dest="wildcards", action="store_true",
                          help="Expand wildcards in basedirs")
        parser.add_option("--xml",
                          dest="output_format", action="store_const", const="xml",
                          help="XML output")

        (options, args) = parser.parse_args(argv)
        self.options = options

        # validate options
        if options.mp3_min_bit_rate is not None:
            if options.mp3_min_bit_rate < 1 or \
              options.mp3_min_bit_rate > 320:
                die("Bitrate must be greater than 0 and less than or equal", \
                    "to 320", 2)
            options.mp3_min_bit_rate *= 1000
        else:
            options.mp3_min_bit_rate = 0

        for index in range(0, len(options.exclude_paths)):
            path = options.exclude_paths[index]
            if path[-1] == os.sep:
                path = path[:-1]
            if not os.path.isdir(path):
                die("There is no directory '%s'" % path, 2)
            options.exclude_paths[index] = path

        if options.prefer_tag not in [1, 2]:
            die("Invalid argument to --prefer-tag or -P", 2)

        # open file for redirection
        if options.outfile:
            mode = 'w'
            if options.output_format == 'db':
                mode += 'b'
            self.set_outstream(options.outfile, mode)

        # add basedirs to both self.Folder and self.ExcludePaths
        for glob_dir in args:
            self.Folders += self.expand(glob_dir)
        self.Folders = filter(lambda x: x not in options.exclude_paths,
                              self.Folders)
        options.exclude_paths += self.Folders

        # options overriding eachother
        if options.debug or not self.OutStream.isatty():
            options.quiet = True
        if options.debug:
            options.list_bad = True
    
        # format outputstring
        self.process_outputstring()

    def set_outstream(self, file, filemode):
        """open output stream for writing"""
        try:
            self.OutStream = open(file, filemode)
        except IOError, (errno, errstr):
            msg = "I/O Error(%s): %s\nCannot open '%s' for writing" % \
                  (errno, errstr, file)
            die(msg, 2)

    def expand(self, dir):
        """translate a basedir to a list of absolute paths"""
        if self.options.wildcards and re.search("[*?]|(?:\[.*\])", dir):
            list = map(os.path.abspath, self.sort(glob.glob(dir)))
        else:
            list = [ os.path.abspath(dir) ]
        return filter(dir_test, list)

    def process_outputstring(self):
        parts = re.split(r"(?<!\\)\[", unescape(self.options.raw_output_string))
        parts = map(lambda x: x.replace(r"\[", "["), parts)
        self.OutputString = unescape_brackets(parts[0])
        for segment in parts[1:]:
            try:
                fieldstr, text = tuple(re.split(r"(?<!\\)]", segment))
            except:
                die("Bad format string", 2)
            self.OutputString += "%s" + unescape_brackets(text)
            self.Fields.append(parse_field(unescape_brackets(fieldstr)))

    def sort(self, list):
        if self.options.ignore_case:
            list.sort(lambda x,y: cmp(x.lower(), y.lower()))
        else:
            list.sort()
        return list

    def cmp_munge(self, basename):
        if self.options.ignore_case:
            return basename.lower()
        else:
            return basename

    def indent(self, basename, depth):
        return " " * self.options.indent * depth + basename


class Column:
    formatter_table = {
        "b": lambda data, depth: to_human(data, 1000.0),
        "l": lambda data, depth: to_minutes(data),
        "m": lambda data, depth: time.ctime(data),
        "n": lambda data, depth: conf.indent(data, depth),
        "s": lambda data, depth: to_human(data),
    }
    attr_table = {
        "a": ('audiolist_format', 'Bitrate(s)'),
        "A": ('artist', 'Artist'),
        "b": ('bitrate', 'Bitrate'),
        "B": ('bitrate', 'Bitrate'),
        "C": ('album', 'Album'),
        #"d": "Dir",
        "D": ('depth', 'Depth'),
        "f": ('num_files', 'Files'),
        "l": ('length', 'Length'),
        "L": ('length', 'Length'),
        "m": ('modified', 'Modified'),
        "M": ('modified', 'Modified'),
        "n": ('name', 'Album/Artist'),
        "N": ('name', 'Album/Artist'),
        "p": ('profile', 'Profile'),
        "P": ('path', 'Path'),
        "q": ('quality', 'Quality'),
        "s": ('size', 'Size'),
        "S": ('size', 'Size'),
        "t": ('mediatype', 'Type'),
        "T": ('brtype', 'BR Type'),
    }
 
    def __init__(self, tag, width, suffix):
        self.width, self.suffix = width, suffix
        if tag in self.formatter_table:
            self.formatter = self.formatter_table[tag]
        else:
            self.formatter = lambda x,y: x
        self.attr, self.name = self.attr_table[tag]

    def _format(self, data, suffixes):
        if suffixes:
            if data:
                data += self.suffix
            else:
                data = ' ' * len(self.suffix)
        if self.width != None:
            data = "%*.*s" % (self.width, abs(self.width), data)
        return data

    def header(self, suffixes=True):
        return self._format(self.name, suffixes)

    def get(self, adir):
        return getattr(adir, self.attr)

    def get_formatted(self, adir, suffixes=True):
        data = self.get(adir)
        if data is None:
            data = ''
        else:
            data = self.formatter(data, adir.depth)
        return self._format(data, suffixes)


def parse_field(field_string):
    tag, width, suffix = (field_string.split(",") + ["", ""])[:3]
    if width == "":
        width = None
    else:
        width = string.atoi(width)
    return Column(tag, width, suffix)


def unescape_part(part):
    r"""unescape the \t and \n sequences of a string"""
    return part.replace(r"\t", "\t").replace(r"\n", "\n")


def unescape(str):
    r"""unescape the \t, \n and \\ sequences of a string"""
    return string.join(map(unescape_part, str.split(r"\\")), "\\")


def unescape_brackets(str):
    return str.replace(r"\[", "[").replace(r"\]", "]")


conf = Settings()
