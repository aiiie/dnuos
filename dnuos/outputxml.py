#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# This program is under GPL license. See COPYING file for details.
#
# Copyright 2006,2007
# Mattias Päivärinta <pejve@vasteras2.net>
#
# Authors
# Mattias Päivärinta <pejve@vasteras2.net>

"""
Module for rendering xml output.
"""


from itertools import chain
from time import localtime
from time import strftime
from xml.sax.saxutils import escape

from misc import intersperse


class Renderer:
    def __init__(self, columns):
        self.columns = columns
        self.indent = ''

    def render(self, dirs, options, data):
        """Render directories to a sequence of strings."""
        output = [
            (lambda: options.disp_date,
             self.render_date()),
            (lambda: True,
             self.render_directories(dirs)),
            (lambda: data.bad_files,
             self.render_bad_files(data.bad_files)),
            (lambda: options.disp_time,
             self.render_generation_time(data.elapsed_time)),
            (lambda: options.disp_result,
             self.render_sizes(data.size)),
            (lambda: options.disp_version,
             self.render_version(data.version['dnuos'])),
        ]
        output = [ renderer for predicate, renderer in output if predicate() ]
        #output = intersperse(output, iter(["-"]))
        return chain(*output)

    def attributes(self, dct):
        attrs = [ ' %s="%s"' % item for item in dct.items() ]
        return ''.join(attrs)

    def tag(self, name, value):
        value = escape(str(value))
        return self.indent + "<%s>%s</%s>" % (name, value, name)

    def tag_start(self, name, **kwargs):
        result = self.indent + "<%s%s>" % (name, self.attributes(kwargs))
        self.indent += '  '
        return result

    def tag_end(self, name):
        self.indent = self.indent[:-2]
        return self.indent + "</%s>" % name

    def render_date(self):
        value = strftime("%Y-%m-%d %H:%M:%S", localtime())
        yield self.tag('date', value)

    def render_directories(self, dirs):
        yield self.tag_start('tree')
        for adir in dirs:
            yield self.tag_start('dir', path=adir.relpath)
            for col in self.columns:
                yield self.tag(col.attr, col.get(adir))
            yield self.tag_end('dir')
        yield self.tag_end('tree')

    def render_bad_files(self, bad_files):
        yield self.tag_start('bad_files')
        for path in bad_files:
            yield self.tag('file', path)
        yield self.tag_end('bad_files')

    def render_generation_time(self, elapsed_time):
        yield self.tag('elapsed_time', elapsed_time)

    def render_sizes(self, sizes):
        yield self.tag_start('sizes')
        for mediatype in ["Ogg", "MP3", "MPC", "AAC", "FLAC"]:
            if sizes[mediatype]:
                yield self.tag_start('mediatype', type=mediatype)
                yield self.tag('size', sizes[mediatype])
                yield self.tag_end('mediatype')
        yield self.tag_end('sizes')

    def render_version(self, version):
        yield self.tag('version', version)
