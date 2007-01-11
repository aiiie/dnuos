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
from optparse import OptionGroup
from optparse import OptionValueError
from optparse import OptionParser, Option
import os
import re
import string
import sys
import time

from misc import die
from misc import to_human


def set_db_format(option, opt_str, value, parser):
    parser.values.outfile = value
    parser.values.output_format = 'db'


def set_format_string(option, opt_str, value, parser):
    try:
        parser.values.format_string, parser.values.fields = \
            parse_format_string2(value)
    except ValueError:
        raise OptionValueError("Bad format string argument to %s" % opt_str)


def set_mp3_min_bitrate(option, opt_str, value, parser):
    if value >= 0 and value <= 320:
        parser.values.mp3_min_bit_rate = 1000 * value
    else:
        raise OptionValueError("Bitrate must be 0 or in the range (1..320)")


def set_preferred_tag(option, opt_str, value, parser):
    if value in [1, 2]:
        parser.values.prefer_tag = value
    else:
        raise OptionValueError("Invalid argument to %s" % opt_str)


def add_exclude_dir(option, opt_str, value, parser):
    if value[-1] == os.sep:
        value = value[:-1]
    if os.path.isdir(value):
        parser.values.exclude_paths.append(value)
    else:
        raise OptionValueError("There is no directory '%s'" % value)


def parse_format_string(data):
    r"""Extract field strings from input, replacing them with %s

    >>> parse_format_string('abcde')
    ('abcde', [])
    >>> parse_format_string('[a]bcde')
    ('%sbcde', ['a'])
    >>> parse_format_string('ab[c]de')
    ('ab%sde', ['c'])
    >>> parse_format_string('a[b]c[d]e')
    ('a%sc%se', ['b', 'd'])
    >>> parse_format_string(r'ab\[c]de')
    ('ab[c]de', [])
    >>> parse_format_string(r'ab\\[c]de')
    ('ab\\%sde', ['c'])
    >>> parse_format_string(r'ab\\\[c]de')
    ('ab\\[c]de', [])
    >>> parse_format_string(r'ab\\\\[c]de')
    ('ab\\\\%sde', ['c'])
    """
    even_backslashes = r'(?:^|[^\\])(?:\\\\)*'
    fieldRE = re.compile(r'(?P<backslashes>%s)\[(?P<field>.*?%s)\]' % \
                         (even_backslashes, even_backslashes))

    fields = []
    match = fieldRE.search(data)
    while match:
        fields.append(match.group('field'))
        data = fieldRE.sub(r'\1%s', data, 1)
        match = fieldRE.search(data)

    return data, fields


def parse_format_string2(data):
    """--output format string -> (python format string, Column instances)

    This is a wrapper for parse_format_string() unescaping the format string
    and making Column instances from the field strings.
    """
    format, fields = parse_format_string(data)
    return unescape(format), map(lambda x: parse_field(unescape(x)), fields)


def to_minutes(value):
    return "%i:%02i" % (value / 60, value % 60)


class Settings:
    def __init__(self):
        self.OutStream = sys.__stdout__

    def parse_args(self, argv=sys.argv[1:]):
        default_format_string="[n,-52]| [s,5] | [t,-4] | [q]"
        format_string, fields = parse_format_string2(default_format_string)
        usage = "%prog [options] basedir ..."
        parser = OptionParser(usage)
        parser.set_defaults(mp3_min_bit_rate=0,
                            bg_color="white",
                            ignore_case=False,
                            indent=4,
                            debug=False,
                            disp_version=False,
                            disp_time=False,
                            disp_date=False,
                            disp_result=False,
                            exclude_paths=[],
                            format_string=format_string,
                            fields=fields,
                            list_bad=True,
                            merge=False,
                            no_cbr=False,
                            no_non_profile=False,
                            outfile=None,
                            output_format="plaintext",
                            prefer_tag=2,
                            quiet=False,
                            stripped=False,
                            text_color="black",
                            wildcards=False)

        group = OptionGroup(parser, "Application")
        group.add_option("--debug",
                         dest="debug", action="store_true",
                         help="Output debug trace to stderr")
        group.add_option("--ignore-bad",
                         dest="list_bad", action="store_false",
                         help="Don't list files that cause Audiotype failure")
        group.add_option("-q", "--quiet",
                         dest="quiet", action="store_true",
                         help="Omit progress indication")
        group.add_option("-V", "--version",
                         dest="disp_version", action="store_true",
                         help="Display version")
        parser.add_option_group(group)

        group = OptionGroup(parser, "Directory walking")
        group.add_option("-e", "--exclude",
                         action="callback", nargs=1, callback=add_exclude_dir, type="string",
                         help="Exclude DIR from search", metavar="DIR")
        group.add_option("-i", "--ignore-case",
                         dest="ignore_case", action="store_true",
                         help="Case-insensitive directory sorting")
        group.add_option("-m", "--merge",
                         dest="merge", action="store_true",
                         help="Parse basedirs in parallell as opposed to one after the other")
        group.add_option("-w", "--wildcards",
                         dest="wildcards", action="store_true",
                         help="Expand wildcards in basedirs")
        parser.add_option_group(group)

        group = OptionGroup(parser, "Filtering")
        group.add_option("-b", "--bitrate",
                         action="callback", nargs=1, callback=set_mp3_min_bitrate, type="int",
                         help="Exclude MP3s with bitrate lower than MIN (in Kbps)", metavar="MIN")
        group.add_option("-l", "--lame-only",
                         dest="no_non_profile", action="store_true",
                         help="Exclude MP3s with no LAME profile")
        group.add_option("-v", "--vbr-only",
                         dest="no_cbr", action="store_true",
                         help="Exclude MP3s with constant bitrates")
        parser.add_option_group(group)

        group = OptionGroup(parser, "Parsing")
        group.add_option("-L", "--lame-old-preset",
                         dest="force_old_lame_presets", action="store_true",
                         help='Report "--alt-preset xxx" for "-V x" LAME MP3s where applicable')
        group.add_option("-P", "--prefer-tag",
                         action="callback", nargs=1, callback=set_preferred_tag, type="int",
                         help="If both ID3v1 and ID3v2 tags exist, prefer n (1 or 2) (default %default)", metavar="n")
        parser.add_option_group(group)

        group = OptionGroup(parser, "Output")
        group.add_option("-B", "--bg",
                         dest="bg_color",
                         help="Set HTML background COLOR (default %default)", metavar="COLOR")
        group.add_option("-f", "--file",
                         dest="outfile",
                         help="Write output to FILE", metavar="FILE")
        group.add_option("-H", "--html",
                         dest="output_format", action="store_const", const="html",
                         help="HTML output (deprecated, use --template html)")
        group.add_option("-I", "--indent",
                         dest="indent", type="int",
                         help="Set indent to n (default %default)", metavar="n")
        group.add_option("-o", "--output",
                         action="callback", nargs=1, callback=set_format_string, type="string",
                         help="Set output format STRING used in plain-text and HTML output. Refer to documentation for details on syntax. (default %s)" % default_format_string, metavar="STRING")
        group.add_option("-O", "--output-db",
                         action="callback", nargs=1, callback=set_db_format, type="string",
                         help="Write list in output.db format to FILE (deprecated, use --template db)", metavar="FILE")
        group.add_option("-s", "--strip",
                         dest="stripped", action="store_true",
                         help="Strip output of field headers and empty directories")
        group.add_option("--template",
                         dest="output_format",
                         help="Set output TEMPLATE (default %default)", metavar="TEMPLATE")
        group.add_option("-T", "--text",
                         dest="text_color",
                         help="Set HTML text COLOR (default %default)", metavar="COLOR")
        parser.add_option_group(group)

        group = OptionGroup(parser, "Statistics")
        group.add_option("-D", "--date",
                         dest="disp_date", action="store_true",
                         help="Display datestamp header")
        group.add_option("-S", "--stats",
                         dest="disp_result", action="store_true",
                         help="Display statistics results")
        group.add_option("-t", "--time",
                         dest="disp_time", action="store_true",
                         help="Display elapsed time footer")
        parser.add_option_group(group)

        (options, args) = parser.parse_args(argv)
        self.options = options

        # add basedirs to both self.Folder and self.ExcludePaths
        options.basedirs = []
        for glob_dir in args:
            options.basedirs += self.expand(glob_dir)
        options.basedirs = filter(lambda x: x not in options.exclude_paths,
                                  options.basedirs)
        options.exclude_paths += options.basedirs

        # options overriding eachother
        if options.debug or not self.OutStream.isatty():
            options.quiet = True
        if options.debug:
            options.list_bad = True

    def expand(self, dir):
        """translate a basedir to a list of absolute paths"""
        if self.options.wildcards and re.search("[*?]|(?:\[.*\])", dir):
            return map(os.path.abspath, self.sort(glob.glob(dir)))
        else:
            return [ os.path.abspath(dir) ]

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


def unescape(data):
    data = data.replace(r'\t', '\t').replace(r'\n', '\n')
    data = re.sub(r'\\([\\\[\]])', r'\1', data)
    return data


conf = Settings()
