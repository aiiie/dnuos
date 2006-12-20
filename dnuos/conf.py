# -*- coding: iso-8859-1 -*-
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


"""
Configuration module for Dnuos.
"""


__version__ = "0.92"


import getopt, glob, os, re, string, sys


class Settings:
    def __init__(self):
        # error messages are the only thing Settings should ever print
        sys.stdout = sys.__stderr__

        self.MP3MinBitRate = 0
        self.BGColor = "white"
        self.IgnoreCase = 0
        self.Indent = 4
        self.Debug = 0
        self.DispVersion = 0
        self.DispTime = 0
        self.DispHelp = 0
        self.DispDate = 0
        self.DispResult = 0
        self.ExcludePaths = []
        self.Folders = {}
        self.ListBad = 1
        self.Merge = 0
        self.OutputDb = 0
        self.Outfile = 0
        self.OutputFormat = "plain"
        self.OutStream = sys.__stdout__
        self.Quiet = 0
        self.TextColor = "black"
        self.Wildcards = 0
        self.RawOutputString = "[n,-52]| [s,5] | [t,-4] | [q]"
        self.Fields = []
        self.OutputString = ""
        self.Stripped = 0
        self.NoCBR = 0
        self.NoNonProfile = 0
        self.ForceOldLAMEPresets = 0

        # parse the command line
        if not self.parse():
            print "Type 'dnuos.py -h' for help."
            sys.exit(2)

        # format outputstring
        self.process_outputstring()

        # direct stdout to the correct stream
        sys.stdout = self.OutStream

    def parse(self):
        shortopts = "b:B:T:p:e:W:f:I:o:P:DhHimO:qStVwcslLv" + "gp:W:"
        longopts = [
            "birate=",
            "bg=",
            "exclude=",
            "date",
            "debug",
            "file=",
            "help",
            "ignore-bad",
            "ignore-case",
            "indent=",
            "lame-old-preset",
            "lame-only",
            "merge",
            "output-db=",
            "output=",
            "prefer-tag=",
            "quiet",
            "stats",
            "strip",
            "text=",
            "time",
            "vbr-only",
            "version",
            "wildcards"] + ["global-sort", "preset=", "width="]
        try:
            opts, args = (getopt.getopt(sys.argv[1:], shortopts, longopts))
        except getopt.GetoptError, (msg, opt):
            print "Invalid option '%s': %s" % (opt, msg)
            return 0

        # parse option pairs
        for o, a in opts:
            if o in ("-b", "--bitrate"):
                self.MP3MinBitRate = string.atoi(a)
                if self.MP3MinBitRate < 1 or self.MP3MinBitRate > 320:
                    print "Bitrate must be greater than 0 and less than or equal to 320"
                    sys.exit(1)
                self.MP3MinBitRate = self.MP3MinBitRate * 1000
            elif o in ("-B", "--bg"): self.BGColor = a
            elif o in ("-D", "--date"): self.DispDate = 1
            elif o == "--debug": self.Debug = 1
            elif o in ("-e", "--exclude"): self.exclude_dir(a)
            elif o in ("-f", "--file"):
                self.Outfile = 1
                self.set_outstream(a, 'w')
            elif o in ("-f", "--file"): self.set_outstream(a)
            elif o in ("-H", "--html"): self.OutputFormat = "HTML"
            elif o in ("-h", "--help"): self.DispHelp = 1
            elif o == "--ignore-bad": self.ListBad = 0
            elif o in ("-i", "--ignore-case"): self.IgnoreCase = 1
            elif o in ("-I", "--indent"): self.Indent = string.atoi(a)
            elif o in ("-l", "--lame-only"): self.NoNonProfile = 1
            elif o in ("-L", "--lame-old-preset"): self.ForceOldLAMEPresets = 1
            elif o in ("-m", "--merge"): self.Merge = 1
            elif o in ("-o", "--output"): self.RawOutputString = a
            elif o in ("-O", "--output-db"):
                if self.Outfile == 1:
                    print "The -f and -O switches may not be used together.\n"
                    sys.exit(1)
                else:
                    self.OutputDb = 1
                    self.set_outstream(a, 'wb')
            elif o in ("-q", "--quiet"): self.Quiet = 1
            elif o in ("-s", "--strip"): self.Stripped = 1
            elif o in ("-S", "--stats"): self.DispResult = 1
            elif o in ("-T", "--text"): self.TextColor = a
            elif o in ("-t", "--time"): self.DispTime = 1
            elif o in ("-v", "--vbr-only"): self.NoCBR = 1
            elif o in ("-V", "--version"): self.DispVersion = 1
            elif o in ("-w", "--wildcards"): self.Wildcards = 1
            elif o in ("-g", "--global-sort",
                       "-p", "--preset",
                   "-W", "--width"):
                print "The '%s' option is no longer supported." % o
                return 0
            else:
                print "This should never happen!"
                print "Unknown option", (o, a)
                return 0

        # add basedirs to both self.Folder and self.ExcludePaths
        self.paircount = 0
        for glob_dir in args:
            dirs = self.expand(glob_dir)
            self.ExcludePaths += dirs
            for key, dir in map(self.add_key, dirs):
                self.add_basedir(key, dir)
        del self.paircount

        # reject "no operation" configurations
        if (not self.Folders
           and not self.DispVersion
           and not self.DispHelp):
            print "No folders to process."
            return 0

        # options overriding eachother
        if self.Debug or not self.OutStream.isatty():
            self.Quiet = 1
        if self.Debug:
            self.ListBad = 1
        return 1
    
    def add_key(self, dir):
        """make a (sortkey, value) pair from a path"""
        if self.Merge:
            key = os.path.basename(dir) or dir
        else:
            self.paircount += 1
            key = "%06d" % self.paircount
        return (key, dir)

    def set_outstream(self, file, filemode):
        """open output stream for writing"""
        try:
            self.OutStream = open(file, filemode)
        except IOError, (errno, errstr):
            print "I/O Error(%s): %s" % (errno, errstr)
            print "Cannot open '%s' for writing" % file
            sys.exit(2)

    def exclude_dir(self, dir):
        """add a directory to exclude-list"""
        if dir[-1] == os.sep:
            dir = dir[:-1]
        if os.path.isdir(dir):
            self.ExcludePaths.append(dir)
        else:
            print "There is no directory '%s'" % dir
            sys.exit(2)

    def expand(self, dir):
        """translate a basedir to a list of absolute paths"""
        if self.Wildcards and re.search("[*?]|(?:\[.*\])", dir):
            list = map(os.path.abspath, self.sort(glob.glob(dir)))
        else:
            list = [ os.path.abspath(dir) ]
        return filter(self.dir_test, list)

    def add_basedir(self, key, dir):
        """add directory with sortkey to self.Folders"""
        if self.Folders.has_key(key):
            self.Folders[key].append(dir)
        else:
            self.Folders[key] = [ dir ]

    def process_outputstring(self):
        parts = re.split(r"(?<!\\)\[", unescape(self.RawOutputString))
        parts = map(lambda x: x.replace(r"\[", "["), parts)
        self.OutputString = unescape_brackets(parts[0])
        for segment in parts[1:]:
            try:
                fieldstr, text = tuple(re.split(r"(?<!\\)]", segment))
            except:
                print "Bad format string"
                sys.exit(2)
            self.OutputString += "%s" + unescape_brackets(text)
            self.Fields.append(parse_field(unescape_brackets(fieldstr)))

    def dir_test(self, dir):
        """check if it's a readable directory"""
        if (not os.path.isdir(dir)
           or not os.access(dir, os.R_OK)
           or dir in self.ExcludePaths):
            return 0

        # does os.access(file, os.R_OK) not work for windows?
        try:
            os.chdir(dir)
            return 1
        except OSError:
            return 0


    def sort(self, list):
        if self.IgnoreCase:
            list.sort(lambda x,y: cmp(x.lower(), y.lower()))
        else:
            list.sort()
        return list

def num_digits(str):
    i = 0
    while i < len(str) and str[i] in string.digits: i += 1
    return i


def parse_num(str):
    len = num_digits(str)
    if len:
        return string.atoi(str[:len]), str[len:]
    else:
        return None, str


def parse_field(str):
    params = (str.split(",") + ["", ""])[:3]
    if params[1] == "": params[1] = None
    else: params[1] = string.atoi(params[1])
    return tuple(params)


def unescape_part(part):
    r"""unescape the \t and \n sequences of a string"""
    return part.replace(r"\t", "\t").replace(r"\n", "\n")


def unescape(str):
    r"""unescape the \t, \n and \\ sequences of a string"""
    return string.join(map(unescape_part, str.split(r"\\")), "\\")


def unescape_brackets(str):
    return str.replace(r"\[", "[").replace(r"\]", "]")


def init():
    global conf
    conf = Settings()
