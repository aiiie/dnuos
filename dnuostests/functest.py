"""
A module for printing unified diffs of dnuos execution per specified parameters
compared to an expected result.
"""

import difflib
import os
import sys
from cStringIO import StringIO
from glob import glob

import dnuos


def _flatten(seq, ltypes=(list, tuple)):
    """From: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/363051"""

    i = 0
    # len(seq) is eval'd each time --
    # no need for maxint with
    # try...except, just run to
    # the dynamic size of the list
    while i < len(seq):
        if len(seq[i]) == 0: # skip empty lists/tuples
            seq.pop(i)
            continue
        while isinstance(seq[i], ltypes):
            seq[i:i+1] = list(seq[i])
        i += 1
    return seq


def process_args(args, no_glob=False):
    """Expands basedirs.

    Basedirs are glob-expanded and prepended with the contents of the $DATA_DIR
    environment variable.
    """

    datadir = os.environ['DATA_DIR']
    args = args.split()
    opts = [opt for opt in args if opt.startswith('-')]
    if no_glob:
        bases = _flatten([os.path.join(datadir, base)
                          for base in args if not base.startswith('-')])
    else:
        bases = _flatten([glob(os.path.join(datadir, base))
                          for base in args if not base.startswith('-')])
    bases.sort()
    return opts + bases


def get_unified_diff(data1, data2):
    """Calculates a unified diff of two strings"""

    data1 = data1.strip().splitlines(1)
    data2 = data2.strip().splitlines(1)
    if (data1, data2) == ([], []):
        return ''
    lines = difflib.unified_diff(data1, data2)
    return ''.join(lines).rstrip('\n')


def write_dnuos_diff(args, expected, no_glob=False):
    """Compares an expected result with dnuos output on given parameters"""

    old = sys.argv, sys.stderr, sys.stdout
    old_cwd = os.getcwd()
    os.chdir(os.environ['DATA_DIR'])
    try:
        output = StringIO()
        sys.argv = ['dnuos', '--disable-cache'] + process_args(args, no_glob)
        sys.stderr = sys.stdout = output
        dnuos.main(locale='C')
        output = output.getvalue()
        try:
            assert output == expected
        except AssertionError:
            sys.stdout.write(get_unified_diff(expected, output))
    finally:
        sys.argv, sys.stderr, sys.stdout = old
        os.chdir(old_cwd)
