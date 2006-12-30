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


class Renderer:
    def render(self, dirs, options, data):
        for adir in dirs:
            chunk = "%d:'%s',%d:'%s',%d:'%s',%d:'%s',%d,%.d,%d" % (
                len(str(adir.get('A'))),
                str(adir.get('A')),
                len(str(adir.get('C'))),
                str(adir.get('C')),
                len(str(adir.get('t'))),
                str(adir.get('t')),
                len(str(adir.get('p'))),
                str(adir.get('p')),
                adir.get('f'),
                adir.get('B') / 1000,
                adir.get('L')
            )
            yield chunk
