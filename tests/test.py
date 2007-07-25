#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# vim: tabstop=4 expandtab shiftwidth=4

import os
import sys


basedir =os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))

os.environ['DATA_DIR'] = os.path.join(basedir, 'tests', 'testdata')


def unit_tests():
  print "Unit tests"
  print "=========="
  old_dir = os.getcwd()
  os.chdir(os.path.join(basedir, 'dnuos'))
  rv = os.system('nosetests --with-doctest -v "%s/dnuos"' % basedir)
  os.chdir(old_dir)
  return rv == 0


def func_doctests():
  print "Functional tests"
  print "================"
  old_dir = os.getcwd()
  os.chdir(os.path.join(basedir, 'tests'))
  rv = os.system('nosetests --with-doctest -v "%s/tests/functional"' % basedir)
  os.chdir(old_dir)
  return rv == 0


def main():
  unit_tests() and func_doctests()


if __name__ == '__main__':
  main()
