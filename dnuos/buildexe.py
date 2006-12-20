#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Script for building a win32 executable from Dnuos.
#
# This program is under GPL license. See COPYING file for details.
#
# Copyright 2003
# Sylvester Johansson  <sylvestor@telia.com>
# Mattias Päivärinta   <pejve@vasteras2.net>


# buildexe.py
# Use this script to build a dnuos win32 exe-file.
# Needs the py2exe module (http://starship.python.net/crew/theller/py2exe/)
# Normally built by running: buildexe.py py2exe -O2 -c -b 1
from distutils.core import setup
import py2exe

setup(name="dnuos", console=["dnuos.py"])
