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


class Renderer(object):
    def render(self, dirs, options, data):
        for adir in dirs:
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
