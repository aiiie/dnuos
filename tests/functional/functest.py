"""
A module for printing unified diffs of dnuos execution per specified parameters
compared to an expected result.
"""

from cStringIO import StringIO
import difflib
from glob import glob
import sys
import os

sys.path.append(os.path.abspath('..'))

import dnuos


def _flatten(seq, ltypes=(list, tuple)):
    """
    From: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/363051
    """
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


def process_args(args):
    """Expands basedirs

    Basedirs are glob-expanded and prepended with the contents of the $DATA_DIR
    environment variable.
    """
    datadir = os.environ.get("DATA_DIR")
    args = args.split()
    opts = [ opt
             for opt in args if opt.startswith('-') ]
    bases = [ glob(os.path.join(datadir, base))
              for base in args if not base.startswith('-') ]
    return opts + _flatten(bases)


def get_unified_diff(data1, data2):
    """Calculates a unified diff of two strings"""
    data1 = data1.strip().splitlines(1)
    data2 = data2.strip().splitlines(1)
    if (data1, data2) == ([], []):
        return ''
    lines = difflib.unified_diff(data1, data2)
    return ''.join(lines).rstrip('\n')


def write_dnuos_diff(args, expected):
    """Compares an expected result with dnuos output on given parameters"""
    output = StringIO()
    old = sys.argv, sys.stderr, sys.stdout
    sys.argv = ['dnuos', '--disable-cache'] + process_args(args)
    sys.stderr = sys.stdout = output
    dnuos.main()
    sys.argv, sys.stderr, sys.stdout = old
    output = get_unified_diff(expected, output.getvalue())
    sys.stdout.write(output)
