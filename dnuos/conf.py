"""Configuration module for Dnuos"""

import glob
import locale
import os
import re
import sys
import optparse
from optparse import OptionGroup, OptionParser, OptionValueError

try:
    set
except NameError:
    from sets import Set as set

import dnuos.output
import dnuos.output.db
import dnuos.output.html
import dnuos.output.plaintext
from dnuos import appdata
from dnuos.misc import deprecation, _

optparse._ = _

def print_help(option, opt_str, value, parser):
    """Prints help and exits program"""

    print parser.format_help()
    sys.exit()


def exit_with_output_help(option, opt_str, value, parser):
    """Prints output help and exits program"""

    print _(r"""
Anything enclosed by brackets is considered a field. A field must have the
following syntax:
  [TAG]
  [TAG,WIDTH]
  [TAG,WIDTH,SUFFIX]
  [TAG,,SUFFIX]

TAG is any of the following characters:
  a  list of bitrates in Audiolist compatible format
  A  artist name as found in ID3 tags
  b  bitrate with suffix (e.g. 192k)
  B  bitrate in bps
  C  album name as found in ID3 tags
  f  number of audio files (including spacers)
  l  length in minutes and seconds
  L  length in seconds
  m  time of last change
  M  time of last change in seconds since the epoch
  n  directory name (indented)
  N  directory name
  p  profile
  P  full path
  q  quality
  s  size with suffix (e.g 65.4M)
  S  size in bytes
  t  file type
  T  bitrate type:
       ~ mixed files
       C constant bitrate
       L lossless compression
       V variable bitrate
  V  encoder

WIDTH defines the exact width of the field. The output is cropped to this
width if needed. Negative values will give left aligned output. Cropping is
always done on the right.

SUFFIX lets you specify a unit to be concatenated to all non-empty data.

Other interpreted sequences are:
  \[  [
  \]  ]
  \n  new line
  \t  tab character

Unescaped brackets are forbidden unless they define a field.

Note: If you have any whitespace in your output string you must put it inside
quotes or otherwise it will not get parsed right.
""")
    sys.exit()


def set_db_format(option, opt_str, value, parser):

    parser.values.outfile = value
    parser.values.output_module = dnuos.output.db
    deprecation(_('The %s option is deprecated and will be removed in a '
                  'future version. Use --template=db --file=FILE instead to '
                  'ensure compatibility with future versions.') % opt_str)


def set_format_string(option, opt_str, value, parser):

    try:
        parser.values.format_string, parser.values.fields = (
            parse_format_string2(value))
    except ValueError:
        raise OptionValueError(_('Bad format string argument to %s')
                               % opt_str)


def set_html_format(option, opt_str, value, parser):

    parser.values.output_module = dnuos.output.html
    deprecation(_('The %s option is deprecated and will be removed in a '
                  'future version. Use --template=html instead to ensure '
                  'compatibility with future versions.') % opt_str)


def set_mp3_min_bitrate(option, opt_str, value, parser):

    if value >= 0 and value <= 320:
        parser.values.mp3_min_bit_rate = 1000 * value
    else:
        raise OptionValueError(_('Bitrate must be 0 or in the range (1..320)'))


def set_output_module(option, opt_str, value, parser):

    try:
        module = getattr(dnuos.output, value)
    except AttributeError:
        raise OptionValueError(_("Unknown template %s") % value)
    parser.values.output_module = module


def set_preferred_tag(option, opt_str, value, parser):

    if value in [1, 2]:
        parser.values.prefer_tag = value
    else:
        raise OptionValueError(_("Invalid argument to %s") % opt_str)


def set_cache_dir(option, opt_str, value, parser):

    parser.values.cache_dir = os.path.expanduser(value)


def set_unknown_types(option, opt_str, value, parser):

    parser.values.unknown_types = tuple(set([v.strip().lower() for v in
                                             value.split(',') if v.strip()]))


def add_exclude_dir(option, opt_str, value, parser):

    if value[-1] == os.sep:
        value = value[:-1]
    if os.path.isdir(value):
        value = os.path.abspath(value)
        parser.values.exclude_paths.append(value)
    else:
        raise OptionValueError(_("No such directory %s") % value)


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
    field_re = re.compile(r'(?P<backslashes>%s)\[(?P<field>.*?%s)\]' %
                          (even_backslashes, even_backslashes))

    fields = []
    match = field_re.search(data)
    while match:
        fields.append(match.group('field'))
        data = field_re.sub(r'\1%s', data, 1)
        match = field_re.search(data)

    return data, fields


def parse_format_string2(data):
    """--output format string -> (python format string, Column instances)

    This is a wrapper for parse_format_string() unescaping the format string
    and making Column instances from the field strings.
    """

    format, fields = parse_format_string(data)
    return unescape(format), [unescape(f) for f in fields]


def parse_args(argv=sys.argv):

    default_format_string = "[n,-52]| [s,5] | [t,-4] | [q]"
    format_string, fields = parse_format_string2(default_format_string)
    usage = _('%prog [options] basedir ...')
    parser = OptionParser(usage, add_help_option=False)
    parser.set_defaults(bg_color="white",
                        cache_dir=appdata.user_data_dir('Dnuos', 'Dnuos'),
                        cull_cache=False,
                        debug=False,
                        delete_cache=False,
                        disp_date=False,
                        disp_result=False,
                        disp_time=False,
                        disp_version=False,
                        exclude_paths=[],
                        fields=fields,
                        format_string=format_string,
                        indent=4,
                        list_bad=True,
                        list_files=False,
                        merge=False,
                        mp3_min_bit_rate=0,
                        no_cbr=False,
                        no_mixed=False,
                        no_non_profile=False,
                        outfile=None,
                        output_module=dnuos.output.plaintext,
                        prefer_tag=2,
                        show_progress=True,
                        sort_key=None,
                        stripped=False,
                        text_color="black",
                        use_cache=True,
                        unknown_types=(),
                        wildcards=False)

    parser.add_option("-h", "--help",
                      action="callback", callback=print_help,
                      help=_("Show this help message and exit"))
    parser.add_option("--help-output-string",
                      action="callback", nargs=0,
                      callback=exit_with_output_help,
                      help=_('Show output string help message'))

    group = OptionGroup(parser, _('Application'))
    group.add_option("--debug",
                     dest="debug", action="store_true",
                     help=_('Output debug trace to stderr'))
    group.add_option("--ignore-bad",
                     dest="list_bad", action="store_false",
                     help=_("Don't list files that cause Audiotype failure"))
    group.add_option("-q", "--quiet",
                     dest="show_progress", action="store_false",
                     help=_('Omit progress indication'))
    group.add_option("-V", "--version",
                     dest='disp_version', action='store_true',
                     help=_('Display version'))
    parser.add_option_group(group)

    group = OptionGroup(parser, _('Caching'))
    group.add_option("--cache-dir",
                     action="callback", nargs=1,
                     callback=set_cache_dir, type="string",
                     help=_('Store cache in DIR (default %s)') % (
                     parser.defaults['cache_dir']),
                     metavar=_('DIR'))
    group.add_option('--cull-cache',
                     dest='cull_cache', action='store_true',
                     help=_('Cull non-existent cached directories and exit'))
    group.add_option('--delete-cache',
                     dest='delete_cache', action='store_true',
                     help=_('Delete the cache directory and exit'))
    group.add_option("--disable-cache",
                     dest="use_cache", action="store_false",
                     help=_('Disable caching'))
    parser.add_option_group(group)


    group = OptionGroup(parser, _('Directory walking'))
    group.add_option("-e", "--exclude",
                     action="callback", nargs=1,
                     callback=add_exclude_dir, type="string",
                     help=_('Exclude DIR from search'), metavar=_('DIR'))
    group.add_option("-i", "--ignore-case",
                     dest="sort_key", action="store_const",
                     const=lambda a, b: locale.strcoll(a.lower(), b.lower()),
                     help=_('Case-insensitive directory sorting'))
    group.add_option('-L', '--list-files',
                     dest='list_files', action='store_true',
                     help=_("List audio files in directories (doesn't use "
                            "caching)"))
    group.add_option("-m", "--merge",
                     dest="merge", action="store_true",
                     help=_('Parse basedirs in parallel and merge output'))
    group.add_option('-u', '--unknown-types',
                     action='callback', nargs=1,
                     callback=set_unknown_types, type='string',
                     help=_('A comma-separated list of unknown audio types '
                            'to list'), metavar=_('TYPES'))
    group.add_option("-w", "--wildcards",
                     dest="wildcards", action="store_true",
                     help=_('Expand wildcards in basedirs'))
    parser.add_option_group(group)

    group = OptionGroup(parser, _('Filtering'))
    group.add_option("-b", "--bitrate",
                     action="callback", nargs=1,
                     callback=set_mp3_min_bitrate, type="int",
                     help=_('Exclude MP3s with bitrate lower than MIN '
                     '(in Kbps)'), metavar=_('MIN'))
    group.add_option("-l", "--lame-only",
                     dest="no_non_profile", action="store_true",
                     help=_('Exclude MP3s with no LAME profile'))
    group.add_option("-v", "--vbr-only",
                     dest="no_cbr", action="store_true",
                     help=_('Exclude MP3s with constant bitrates'))
    group.add_option("-M", "--no-mixed",
                     dest="no_mixed", action="store_true",
                     help=_('Exclude directories with mixed files'))
    parser.add_option_group(group)

    group = OptionGroup(parser, _('Output'))
    group.add_option("-B", "--bg",
                     dest="bg_color",
                     help=_('Set HTML background COLOR (default %s)') % (
                     parser.defaults['bg_color']),
                     metavar=_('COLOR'))
    group.add_option("-f", "--file",
                     dest="outfile",
                     help=_('Write output to FILE'), metavar=_('FILE'))
    group.add_option("-H", "--html",
                     action="callback", nargs=0, callback=set_html_format,
                     help=_('HTML output (deprecated, use --template html)'))
    group.add_option("-I", "--indent",
                     dest="indent", type="int",
                     help=_('Set indent to n (default %s)') % (
                     parser.defaults['indent']),
                     metavar=_('n'))
    group.add_option("-o", "--output",
                     action="callback", nargs=1,
                     callback=set_format_string, type="string",
                     help=_('Set output format STRING used in plain-text '
                     'and HTML output. See --help-output-string for '
                     'details on syntax. (default %s)') %
                     default_format_string, metavar=_('STRING'))
    group.add_option("-O", "--output-db",
                     action="callback", nargs=1,
                     callback=set_db_format, type="string",
                     help=_('Write list in output.db format to FILE '
                     '(deprecated, use --template db)'), metavar=_('FILE'))
    group.add_option("-P", "--prefer-tag",
                     action="callback", nargs=1,
                     callback=set_preferred_tag, type="int",
                     help=_('If both ID3v1 and ID3v2 tags exist, prefer '
                     'n (1 or 2) (default %s)') % (
                     parser.defaults['prefer_tag']),
                     metavar=_('n'))
    group.add_option("-s", "--strip",
                     dest="stripped", action="store_true",
                     help=_('Strip output of field headers and empty '
                     'directories'))
    group.add_option("--template",
                     action="callback", nargs=1,
                     callback=set_output_module, type="string",
                     help=_('Set output TEMPLATE (default plaintext)'),
                     metavar=_('TEMPLATE'))
    group.add_option("-T", "--text",
                     dest="text_color",
                     help=_('Set HTML text COLOR (default %s)') % (
                     parser.defaults['text_color']),
                     metavar=_('COLOR'))
    parser.add_option_group(group)

    group = OptionGroup(parser, _('Statistics'))
    group.add_option("-D", "--date",
                     dest="disp_date", action="store_true",
                     help=_('Display datestamp header'))
    group.add_option("-S", "--stats",
                     dest="disp_result", action="store_true",
                     help=_('Display statistics results'))
    group.add_option("-t", "--time",
                     dest="disp_time", action="store_true",
                     help=_('Display elapsed time footer'))
    parser.add_option_group(group)

    (options, args) = parser.parse_args(argv[1:])

    # add basedirs
    options.basedirs = []
    for glob_dir in args:
        options.basedirs += [p for p in expand(options, glob_dir)
                             if p not in options.exclude_paths
                                and os.path.isdir(p)]
    if not options.basedirs and not (options.cull_cache or
        options.delete_cache):
        if options.disp_version:
            print ''.join(dnuos.output.plaintext.render_version(
                dnuos.__version__))
            sys.exit()
        print >> sys.stderr, (_("No folders to process.\nType `%s -h' "
                                "for help.") % os.path.basename(argv[0]))
        sys.exit(2)

    # options overriding eachother
    if options.debug or (not options.outfile and
                         isinstance(sys.stdout, file) and
                         sys.stdout.isatty()):
        options.show_progress = False
    if options.output_module == dnuos.output.db:
        options.list_bad = False

    return options

def expand(options, dir_):
    """translate a basedir to a list of absolute paths"""

    if options.wildcards and re.search("[*?]|(?:\[.*\])", dir_):
        dirs = glob.glob(dir_)
        dirs.sort(options.sort_key)
        return [os.path.abspath(d) for d in dirs]
    else:
        return [os.path.abspath(dir_)]


def unescape(data):
    """Unescapes escaped backslashes"""

    data = data.replace(r'\t', '\t').replace(r'\n', '\n')
    data = re.sub(r'\\([\\\[\]])', r'\1', data)
    return data
