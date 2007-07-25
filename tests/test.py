#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# vim: tabstop=4 expandtab shiftwidth=4

"""
Runs the test suite of both unit and functional tests
"""

import os
import sys


def unit_tests(basedir):
    """Find and run unit tests in the application code"""
    print "Unit tests"
    print "=========="
    old_dir = os.getcwd()
    os.chdir(os.path.join(basedir, 'dnuos'))
    error_level = os.system('nosetests --with-doctest -v "%s/dnuos"' % basedir)
    os.chdir(old_dir)
    return error_level == 0


def func_doctests(basedir):
    """Run all functional tests in tests/functional"""
    print "Functional tests"
    print "================"
    old_dir = os.getcwd()
    os.chdir(os.path.join(basedir, 'tests'))
    cmd = 'nosetests --with-doctest -v "%s/tests/functional"' % basedir
    error_level = os.system(cmd)
    os.chdir(old_dir)
    return error_level == 0


def main():
    """Run both unit tests and functional tests"""
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
    os.environ['DATA_DIR'] = os.path.join(basedir, 'tests', 'testdata')
    unit_tests(basedir) and func_doctests(basedir)


if __name__ == '__main__':
    main()
