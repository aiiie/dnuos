"""Miscellaneous module for Dnuos.

Most of these things are algorithms for various lowlevel things. Not all
however.

Don't import other Dnuos modules from here.

Feel free to organize this in a better way if you know how. I don't.
"""

import locale
import os
from heapq import heappop, heappush
from itertools import count
from warnings import warn

def _find_locale_dir():

    # Avoid unpacking the egg if translation isn't necessary
    try:
        lang = locale.getdefaultlocale()[0]
    except ValueError:
        return None
    if not lang or lang.split('_', 1)[0] == 'en':
        return None

    # __file__ isn't always available (e.g. in frozen builds)
    if '__file__' in globals():
        locale_dir = os.path.join(os.path.split(__file__)[0], 'locale')
        if os.path.isdir(locale_dir):
            return locale_dir
    return None

try:
    import gettext
    _ = gettext.translation('dnuos', _find_locale_dir(), fallback=True).gettext
except ImportError:
    _ = lambda s: s


class Lookahead(object):
    """Wrapper class for adding one element of lookahead to an iterator.
    Requires iterables of strings or sequences of strings.

    Example behavior:

    >>> x = Lookahead(iter(('0', '1', '2')))
    >>> x.lookahead
    '0'
    >>> x.next()
    '0'
    >>> x.lookahead
    '1'
    >>> x.next()
    '1'
    >>> x.lookahead
    '2'
    >>> y = Lookahead(iter(('1', '2', '3')))
    >>> y.next()
    '1'
    >>> x == y
    True
    >>> y.next()
    '2'
    >>> x <= y
    True
    >>> x.empty
    False
    >>> x.next()
    '2'
    >>> x.empty
    True
    """

    __slots__ = ['iterator', 'sort_cmp', 'lookahead', 'empty']

    def __init__(self, iterator, sort_cmp=cmp):

        self.iterator = iterator
        self.sort_cmp = sort_cmp
        self.lookahead = None
        self.empty = False
        self.next()

    def __iter__(self):

        return self

    def next(self):
        """Get next value"""

        result = self.lookahead
        try:
            self.lookahead = self.iterator.next()
        except StopIteration:
            self.lookahead = None
            self.empty = True
        return result

    def __cmp__(self, other):
        """Compare iterator heads (as opposed to the entire iterators)"""

        return self.sort_cmp(self.lookahead, other.lookahead)


def deprecation(message):

    warn(message, DeprecationWarning, stacklevel=2)


def dir_depth(path):
    """Return the subdirectory depth of a path.

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
    """Return the largest n such that seq1[:n] == seq2[:n].

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


def formatwarning(message, category, filename, lineno):
    """Custom warning formatting."""

    return "%s: %s\n" % (category.__name__, message)


def is_subdir(path1, path2):
    """Returns True if path1 is a subdirectory of path2, otherwise False.

    >>> import os
    >>> os_dir = os.path.dirname(os.__file__)
    >>> above_os = os.path.dirname(os_dir)
    >>> is_subdir(above_os, os_dir)
    False
    >>> is_subdir(os_dir, above_os)
    True
    >>> is_subdir(os_dir, os_dir)
    True
    """

    path1 = path1.split(os.path.sep)
    path2 = path2.split(os.path.sep)
    return path2 == path1[:len(path2)]


def merge(iterators, sort_cmp=cmp):
    """Merge n ordered iterators into one ordered iterator.

    Merge two ordered iterators
    >>> xs = iter(['a1', 'b1', 'c1'])
    >>> ys = iter(['a2', 'b2', 'c2'])
    >>> list(merge([xs, ys]))
    ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']
    """

    # Make a heap of the given iterators. The heap is sorted by the
    # iterator head elements, or if those are equal, by the order of
    # insertion. Thats what the index is for.
    # Heappush and heappop use the __lt__ and __eq__ methods of the
    # elements for the sorting. Generator items dont have meaningful
    # comparison operators, so we wrap them in Lookahead which defines
    # the inequality as per the respective head elements.
    heap = []
    for index in range(0, len(iterators)):
        iterator = Lookahead(iterators[index], sort_cmp)
        if not iterator.empty:
            heappush(heap, (iterator, index))

    # Since all iterators are ordered (precondition) and the heap is ordered
    # by head elements of the iterators, the head element of the head
    # iterator on the heap is the smallest element of all remaining
    # elements, and thus the next element in the ordered merged iteration.
    while heap:
        iterator, index = heappop(heap)
        yield iterator.next()
        if not iterator.empty:
            heappush(heap, (iterator, index))


def to_human(value, radix=1024.0):
    """Convert a value to a string using SI suffixes.

    Example output:

    >>> to_human(20)
    '20.0 '
    >>> to_human(20 * 1024)
    '20.0k'
    >>> to_human(20 * 1024 ** 2)
    '20.0M'
    >>> to_human(20 * 1024 ** 3)
    '20.0G'
    >>> to_human(20 * 1024 ** 4)
    '20480G'
    """

    i = 0
    while value >= radix and i < 3:
        value /= radix
        i += 1
    suffix = " kMG"[i]
    if value > 100:
        value = locale.format('%d', value)
    elif value < 10:
        value = locale.format('%.2f', value)
    else:
        value = locale.format('%.1f', value)
    return "%s%s" % (value, suffix)
