from cStringIO import StringIO
import difflib
from glob import glob
import sys
import os
import dnuos


def _flatten(l, ltypes=(list, tuple)):
    """
    From: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/363051
    """
    i = 0
    # len(l) is eval'd each time --
    # no need for maxint with
    # try...except, just run to
    # the dynamic size of the list
    while i < len(l):
        if len(l[i]) == 0: # skip empty lists/tuples
            l.pop(i)
            continue
        while isinstance(l[i], ltypes):
            l[i:i+1] = list(l[i])
        i += 1
    return l


def process_args(args):
    datadir = os.environ.get("DATA_DIR")
    args = args.split()
    opts = [ opt
             for opt in args if opt.startswith('-') ]
    bases = [ glob(os.path.join(datadir, base))
              for base in args if not base.startswith('-') ]
    return opts + _flatten(bases)


def write_unified_diff(a, b):
    a = a.strip().splitlines(1)
    b = b.strip().splitlines(1)
    if (a, b) == ([], []):
        return ''
    sys.stdout.write(''.join(difflib.unified_diff(a, b)))


def write_dnuos_diff(args, expected):
    output = StringIO()
    old = sys.argv, sys.stderr, sys.stdout
    sys.argv = process_args(args)
    sys.stderr = sys.stdout = output
    dnuos.main()
    sys.argv, sys.stderr, sys.stdout = old
    write_unified_diff(expected, output.getvalue())


if __name__ == '__main__':
    args = ' '.join(sys.argv[1:])
    expected = sys.stdin.read()
    dnuos_diff(args, expected)
