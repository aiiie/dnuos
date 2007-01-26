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
Miscellaneous module for Dnuos.

Most of these things are algorithms for various lowlevel things. Not all
however.
Don't import other Dnuos modules from here.
Feel free to organize this in a better way if you know how. I don't.
"""


from heapq import heappop, heappush
from itertools import count
import os
import sys


class Lookahead(object):
    """Wrapper class for adding one element of lookahead to an iterator"""

    __slots__ = ['iterator', 'lookahead', 'empty']

    def __init__(self, iterator):
        self.iterator = iterator
        self.lookahead = None
        self.empty = False
        self.next()

    def next(self):
        """Get next value"""
        result = self.lookahead
        try:
            self.lookahead = self.iterator.next()
        except StopIteration:
            self.lookahead = None
            self.empty = True
        return result

    def __le__(self, other):
        """Compare iterator heads for (<=) inequality - as opposed to the entire iterators"""
        return self.lookahead <= other.lookahead

    def __eq__(self, other):
        """Compare iterator heads for equality - as opposed to the entire iterators"""
        return self.lookahead == other.lookahead


def die(msg, exitcode):
    """print message and exit with exitcode"""
    print >> sys.stderr, msg
    sys.exit(exitcode)


def dir_depth(path):
    """Return the subdirectory depth of a path

    >>> dir_depth('/')
    0
    >>> dir_depth('/usr')
    1
    >>> dir_depth('/usr/')
    1
    >>> dir_depth('/usr/local')
    2
    """
    parts = os.path.abspath(path).split(os.path.sep)[1:]
    return parts != [''] and len(parts) or 0


def equal_elements(seq1, seq2):
    """Return the largest n such that seq1[:n] == seq2[:n]

    >>> equal_elements('', '')
    0
    >>> equal_elements('abcd', 'abcd')
    4
    >>> equal_elements('abcd', 'abCD')
    2
    >>> equal_elements('abcd', 'abcdef')
    4
    >>> equal_elements('abcdef', 'abcd')
    4
    """
    for index in count():
        try:
            if seq1[index] != seq2[index]:
                return index
        except IndexError:
            return index


def fmap(value, funcs):
    """Feeds the same value to a list of functions

    >>> fmap(-5.5, [str, int, abs])
    ['-5.5', -5, 5.5]
    """
    return [ func(value) for func in funcs ]


def get_outfile(filename):
    """Open file for writing"""
    try:
        return filename and open(filename, 'w') or sys.stdout
    except IOError, (errno, errstr):
        msg = "I/O Error(%s): %s\nCannot open '%s' for writing" % \
              (errno, errstr, file)
        die(msg, 2)


def is_subdir(path1, path2):
    """Returns True if path1 is a subdirectory of path2, otherwise False

    >>> is_subdir('/home', '/usr')
    False
    >>> is_subdir('/usr/local', '/usr')
    True
    >>> is_subdir('/usr', '/usr')
    True
    """
    path1 = path1.split(os.path.sep)
    path2 = path2.split(os.path.sep)
    return path2 == path1[:len(path2)]


def make_included_pred(included, excluded):
    """Create predicate for included but not excluded paths

    >>> pred = make_included_pred(['/etc','/usr'], ['/usr/local'])
    >>> pred('/usr/local')
    False
    >>> pred('/usr/local/share')
    False
    >>> pred('/usr')
    True
    >>> pred('/usr/doc')
    True
    >>> pred('/home')
    False

    >>> pred = make_included_pred([], ['/usr/local'])
    >>> pred('/')
    False

    >>> pred = make_included_pred(['/usr'], [])
    >>> pred('/usr/local/share')
    True
    """
    i_preds = [ lambda path, base=base: is_subdir(path, base)
                for base in included ]
    e_preds = [ lambda path, base=base: is_subdir(path, base)
                for base in excluded ]

    # any() is nicer than max(), but only supported by 2.5+
    return lambda path: ((bool(included) and max(fmap(path, i_preds))) and not
                         (bool(excluded) and max(fmap(path, e_preds))))


def map_dict(func, dict):
    for key in dict.keys():
        dict[key] = func(dict[key])
    return dict


def merge(*iterators):
    """Merge n ordered iterators into one ordered iterator

    Merge two ordered iterators
    >>> xs = iter(['a1', 'b1', 'c1'])
    >>> ys = iter(['a2', 'b2', 'c2'])
    >>> list(merge(xs, ys))
    ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']
    """
    # Make a heap of the given iterators. The heap is sorted by to the head
    # elements. Thus the need for the lookahead.
    heap = []
    for index in range(0, len(iterators)):
        iterator = Lookahead(iterators[index])
        if not iterator.empty:
            heappush(heap, (iterator, index))

    # Since all iterators are ordered (precondition) and the heap is ordered
    # by head elements of the iterators, the head element of the head iterator
    # on the heap is the smallest element of all remaining elements, and thus
    # the next element in the ordered merged iteration.
    while heap:
        iterator, index = heappop(heap)
        yield iterator.next()
        if not iterator.empty:
            heappush(heap, (iterator, index))


def sort(lst, key=lambda x: x):
    """Sort a list by an optional key function

    >>> data = [1, 2, 5, 3, 4]
    >>> sort(data)
    [1, 2, 3, 4, 5]
    >>> data = ['a', 'b', 'e', 'C', 'D']
    >>> sort(data, lambda x: x.lower())
    ['a', 'b', 'C', 'D', 'e']
    """
    deco = [ (key(elem), elem) for elem in lst ]
    deco.sort()
    return [ elem for _, elem in deco ]


def partition(iterable, func):
    """Partition a set of objects into equivalence classes

    Returns a dictionary { func(obj): [equivalent objects] }
    Object o1 and o2 are equivalent if and only if func(o1) == func(o2)

    >>> p = partition(range(0, 10), lambda x: x % 3)

    >>> classes = p.keys()
    >>> classes.sort()
    >>> print classes
    [0, 1, 2]

    >>> print p[0], p[1], p[2]
    [0, 3, 6, 9] [1, 4, 7] [2, 5, 8]
    """
    partitions = { }
    for obj in iterable:
        partitions.setdefault(func(obj), []).append(obj)
    return partitions


def split_dict(dct, pred):
    """Split dictionary in two by a predicate function

    >>> dct = {1:'a', 2:'b', 3:'c'}
    >>> pred = lambda (key, value): key % 2 == 0
    >>> t, f = split_dict(dct, pred)
    >>> t
    {2: 'b'}
    >>> print len(f), 1 in f, 3 in f
    2 True True
    """
    cells = partition(dct.items(), pred)
    return dict(cells.get(True, [])), dict(cells.get(False, []))


def to_human(value, radix=1024.0):
    """Convert a value to a string using SI suffixes"""
    i = 0
    while value >= radix:
        value /= radix
        i += 1
    suffix = " kMG"[i]
    if value > 100:
        return "%d%s" % (value, suffix)
    elif value < 10:
        return "%.2f%s" % (value, suffix)
    else:
        return "%.1f%s" % (value, suffix)


def uniq(list):
    """make a list with all duplicate elements removed"""
    if not list: return []
    list[0] = [ list[0] ]
    return reduce(lambda A,x: x in A and A or A+[x], list)
