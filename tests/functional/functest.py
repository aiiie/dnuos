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
    datadir = os.environ.get("DATA_DIR")
    args = args.split()
    opts = [ opt
             for opt in args if opt.startswith('-') ]
    bases = [ glob(os.path.join(datadir, base))
              for base in args if not base.startswith('-') ]
    return opts + _flatten(bases)


def write_unified_diff(data1, data2):
    data1 = data1.strip().splitlines(1)
    data2 = data2.strip().splitlines(1)
    if (data1, data2) == ([], []):
        return ''
    lines = [ line.rstrip('\n')
              for line in difflib.unified_diff(data1, data2) ]
    sys.stdout.write('\n'.join(lines))


def write_dnuos_diff(args, expected):
    output = StringIO()
    old = sys.argv, sys.stderr, sys.stdout
    sys.argv = ['dnuos', '--disable-cache'] + process_args(args)
    sys.stderr = sys.stdout = output
    dnuos.main()
    sys.argv, sys.stderr, sys.stdout = old
    write_unified_diff(expected, output.getvalue())
