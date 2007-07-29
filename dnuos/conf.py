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

from singleton import Singleton
from misc import deprecation
import output


def stricmp(str1, str2):
    return cmp(str1.lower(), str2.lower())


def set_db_format(option, opt_str, value, parser):
    parser.values.outfile = value
    parser.values.output_module = output.db
    deprecation("The %s option is deprecated and will be removed in a future version. Use --template=db --file=FILE instead to ensure compatibility with future versions." % opt_str)


def set_format_string(option, opt_str, value, parser):
    try:
        parser.values.format_string, parser.values.fields = \
            parse_format_string2(value)
    except ValueError:
        raise OptionValueError("Bad format string argument to %s" % opt_str)


def set_html_format(option, opt_str, value, parser):
    parser.values.output_module = output.html
    deprecation("The %s option is deprecated and will be removed in a future version. Use --template=html instead to ensure compatibility with future versions." % opt_str)


def set_mp3_min_bitrate(option, opt_str, value, parser):
    if value >= 0 and value <= 320:
        parser.values.mp3_min_bit_rate = 1000 * value
    else:
        raise OptionValueError("Bitrate must be 0 or in the range (1..320)")


def set_output_module(option, opt_str, value, parser):
    try:
        module = getattr(output, value)
    except AttributeError:
        raise OptionValueError("Unknown template '%s'" % value)
    parser.values.output_module = module


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
    ('ab\\[c]de', [])
    >>> parse_format_string(r'ab\\[c]de')
    ('ab\\\\%sde', ['c'])
    >>> parse_format_string(r'ab\\\[c]de')
    ('ab\\\\\\[c]de', [])
    >>> parse_format_string(r'ab\\\\[c]de')
    ('ab\\\\\\\\%sde', ['c'])
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
    return unescape(format), map(unescape, fields)


class Settings(Singleton):
    def parse_args(self, argv=sys.argv[1:]):
        default_format_string="[n,-52]| [s,5] | [t,-4] | [q]"
        format_string, fields = parse_format_string2(default_format_string)
        usage = "%prog [options] basedir ..."
        parser = OptionParser(usage)
        parser.set_defaults(bg_color="white",
                            debug=False,
                            disp_date=False,
                            disp_result=False,
                            disp_time=False,
                            disp_version=False,
                            exclude_paths=[],
                            fields=fields,
                            format_string=format_string,
                            indent=4,
                            list_bad=True,
                            merge=False,
                            mp3_min_bit_rate=0,
                            no_cbr=False,
                            no_non_profile=False,
                            outfile=None,
                            output_module=output.plaintext,
                            prefer_tag=2,
                            show_progress=True,
                            sort_key=None,
                            stripped=False,
                            text_color="black",
                            use_cache=True,
                            wildcards=False)

        group = OptionGroup(parser, "Application")
        group.add_option("--debug",
                         dest="debug", action="store_true",
                         help="Output debug trace to stderr")
        group.add_option("--ignore-bad",
                         dest="list_bad", action="store_false",
                         help="Don't list files that cause Audiotype failure")
        group.add_option("-q", "--quiet",
                         dest="show_progress", action="store_false",
                         help="Omit progress indication")
        group.add_option("-V", "--version",
                         dest="disp_version", action="store_true",
                         help="Display version")
        parser.add_option_group(group)

        group = OptionGroup(parser, "Directory walking")
        group.add_option("--disable-cache",
                         dest="use_cache", action="store_false",
                         help="Disable caching")
        group.add_option("-e", "--exclude",
                         action="callback", nargs=1, callback=add_exclude_dir, type="string",
                         help="Exclude DIR from search", metavar="DIR")
        group.add_option("-i", "--ignore-case",
                         dest="sort_key", action="store_const", const=stricmp,
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
                         action="callback", nargs=0, callback=set_html_format,
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
                         action="callback", nargs=1, callback=set_output_module, type="string",
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

        # add basedirs to self.Folder
        options.basedirs = []
        for glob_dir in args:
            options.basedirs += [ path for path in self.expand(glob_dir)
                                       if path not in options.exclude_paths ]
        options.exclude_paths += options.basedirs

        # options overriding eachother
        if options.debug or (not options.outfile and
                             isinstance(sys.stdout, file) and
                             sys.stdout.isatty()):
            options.show_progress = False
        if options.output_module == output.db:
            options.list_bad = False

        return options

    def expand(self, dir):
        """translate a basedir to a list of absolute paths"""
        if self.options.wildcards and re.search("[*?]|(?:\[.*\])", dir):
            dirs = sort(glob.glob(dir), self.options.sort_key)
            return map(os.path.abspath, dirs)
        else:
            return [ os.path.abspath(dir) ]


def unescape(data):
    data = data.replace(r'\t', '\t').replace(r'\n', '\n')
    data = re.sub(r'\\([\\\[\]])', r'\1', data)
    return data
