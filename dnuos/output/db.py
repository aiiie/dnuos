# -*- coding: iso-8859-1 -*-
# vim: tabstop=4 expandtab shiftwidth=4
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
            artist    = _db_string(adir.artist)
            album     = _db_string(adir.album)
            mediatype = _db_string(adir.mediatype)
            profile   = _db_string(adir.profile)
            num_files = adir.num_files
            bitrate   = adir.bitrate / 1000
            length    = int(adir.length)
            yield "%s,%s,%s,%s,%d,%.d,%d" % (artist, album, mediatype, profile, num_files, bitrate, length)


def _db_string(data):
    if data is None:
        return "0:''"
    else:
        data = str(data)
        return "%d:'%s'" % (len(data), data)
