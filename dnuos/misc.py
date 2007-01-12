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

Here goes stuff that is not application specific.
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


def get_outfile(filename):
    """Open file for writing"""
    try:
        return filename and open(filename, 'w') or sys.stdout
    except IOError, (errno, errstr):
        msg = "I/O Error(%s): %s\nCannot open '%s' for writing" % \
              (errno, errstr, file)
        die(msg, 2)


def intersperse(items, sep):
    """Separate each pair of elements in an iterable with a separator"""
    iterator = iter(items)
    yield iterator.next()
    for item in iterator:
        yield sep
        yield item


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
