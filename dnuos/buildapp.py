#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Script for building an OS X app package from Dnuos.
#
# This program is under GPL license. See COPYING file for details.
#

# This isn't really useful right now. Running the .app bundle doesn't really
# do much, but you can run the resulting binary that's inside the bundle.
# This is really only around for the upcoming OS X GUI.
# Requires py2app (http://pythonmac.org/wiki/py2app)
from distutils.core import setup
import py2app

setup(
    app=['dnuos.py'],
    options=dict(py2app=dict(optimize=1))
)
