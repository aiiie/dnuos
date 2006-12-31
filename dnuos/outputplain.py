#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# This program is under GPL license. See COPYING file for details.
#
# Copyright 2006
# Mattias Päivärinta <pejve@vasteras2.net>
#
# Authors
# Mattias Päivärinta <pejve@vasteras2.net>

"""
Module for rendering plain-text output.
"""


from itertools import chain

from misc import intersperse


class Renderer:
    def __init__(self, format_string, columns):
        self.format_string = format_string
        self.columns = columns

    def render(self, dirs, options, data):
        """Render directories to a sequence of strings."""
        output = [
            (lambda: options.disp_date,
             self.render_date()),
            (lambda: True,
             self.render_directories(dirs, not options.stripped)),
            (lambda: data.bad_files,
             self.render_bad_files(data.bad_files)),
            (lambda: options.disp_time,
             self.render_generation_time(data.elapsed_time)),
            (lambda: options.disp_result,
             self.render_sizes(data.size, data.elapsed_time)),
            (lambda: options.disp_version,
             render_version(data.version)),
        ]
        output = [ renderer for predicate, renderer in output if predicate() ]
        output = intersperse(output, iter(["-"]))
        return chain(*output)

    def render_date(self):
        yield time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())

    def render_directories(self, dirs, show_headers=True):
        if show_headers:
            fields = map(lambda c: c.header(), self.columns)
            line = self.format_string % tuple(fields)
            yield line
            yield "=" * len(line)

        for adir in dirs:
            fields = map(lambda c: c.get_formatted(adir), self.columns)
            yield self.format_string % tuple(fields)

    def render_bad_files(self, bad_files):
        yield "Audiotype failed on the following files:"
        yield string.join(bad_files, "\n")

    def render_generation_time(self, elapsed_time):
        yield "Generation time:     %8.2f s" % elapsed_time

    def render_sizes(self, sizes, elapsed_time):
        line = "+-----------------------+-----------+"

        yield line
        yield "| Format    Amount (Mb) | Ratio (%) |"
        yield line
        for mediatype in ["Ogg", "MP3", "MPC", "AAC", "FLAC"]:
            if sizes[mediatype]:
                yield "| %-8s %12.2f | %9.2f |" % (
                    mediatype,
                    sizes[mediatype] / (1024 * 1024),
                    sizes[mediatype] * 100 / sizes["Total"])
        yield line
        total_megs = sizes["Total"] / (1024 * 1024)
        yield "| Total %10.2f Mb   |" % total_megs
        yield "| Speed %10.2f Mb/s |" % (total_megs / elapsed_time)
        yield line[:25]


def render_version(versions):
    yield "dnuos version:     %s" % versions['dnuos']
    yield "audiotype version: %s" % versions['audiotype']
