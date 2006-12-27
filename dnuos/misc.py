# -*- coding: iso-8859-1 -*-
#
# This program is under GPL license. See COPYING file for details.
#
# Copyright 2006
# Mattias Päivärinta <pejve@vasteras2.net>
#
# Authors
# Mattias Päivärinta <pejve@vasteras2.net>


import os
import sys


def die(msg, exitcode):
    print >> sys.stderr, msg
    sys.exit(exitcode)


def dir_test(path):
    """check if it's a readable directory"""
    if not os.path.isdir(path) or not os.access(path, os.R_OK):
        return False

    # does os.access(file, os.R_OK) not work for windows?
    try:
        cwd = os.getcwd()
        os.chdir(path)
        os.chdir(cwd)
        return True
    except OSError:
        return False
