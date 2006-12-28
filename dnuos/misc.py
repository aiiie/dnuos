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
import os
import sys


class Lookahead:
    """Wrapper class for adding one element of lookahead to iterators"""
    def __init__(self, iterable):
        self.iterable = iterable
        self.lookahead = None
        self.empty = False
        self.next()

    def next(self):
        """Get next value"""
        result = self.lookahead
        try:
            self.lookahead = self.iterable.next()
        except StopIteration:
            self.lookahead = None
            self.empty = True
        return result

    def __le__(self, other):
        return self.lookahead <= other.lookahead

    def __eq__(self, other):
        return self.lookahead == other.lookahead


def die(msg, exitcode):
    """print message and exit with exitcode"""
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


def intersperse(items, sep):
    """Separate each pair of elements in an iterable with a separator"""
    iterator = iter(items)
    yield iterator.next()
    for item in iterator:
        yield sep
        yield item


def merge(*iterators):
    """Merge n ordered iterators into one ordered iterator"""
    heap = []
    for index in range(0, len(iterators)):
        iterator = Lookahead(iterators[index])
        if not iterator.empty:
            heappush(heap, (iterator, index))

    while heap:
        iterator, index = heappop(heap)
        yield iterator.next()
        if not iterator.empty:
            heappush(heap, (iterator, index))


def subdirs(path, make_key=lambda x: x):
    """Create a sorted iterable of subdirs

    make_key(basename) is used for sort key."""
    subs = [ os.path.join(path, sub) for sub in os.listdir(path) ]
    subs = [ (make_key(os.path.basename(path)), path)
             for path in subs
             if dir_test(path) ]
    subs.sort()
    for key, sub in subs:
        yield sub
