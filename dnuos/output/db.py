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
Module for rendering outputdb format.
"""


from dnuos.output.abstract_renderer import AbstractRenderer


class Renderer(AbstractRenderer):
    def render(self, dir_pairs, options, data):
        for adir, root in dir_pairs:
            chunk = "%d:'%s',%d:'%s',%d:'%s',%d:'%s',%d,%.d,%d" % (
                len(str(adir.album)),
                str(adir.album),
                len(str(adir.artist)),
                str(adir.artist),
                len(adir.mediatype),
                adir.mediatype,
                len(adir.profile),
                adir.profile,
                adir.num_files,
                adir.bitrate / 1000,
                adir.length
            )
            yield chunk
