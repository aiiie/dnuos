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

    try:
        from pkg_resources import resource_filename
        return resource_filename(__name__, 'locale')
    except ImportError:
        if '__file__' in globals():
            locale_dir = os.path.join(os.path.split(__file__)[0], 'locale')
            if os.path.isdir(locale_dir):
                return locale_dir
        return None

import gettext
_ = gettext.translation('dnuos', _find_locale_dir(), fallback=True).ugettext



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
        """Compare iterator heads for (<=) inequality - as opposed to the
        entire iterators.
        """

        # This is a bit sloppy as it never considers the type of the
        # other element
        return self.lookahead <= other.lookahead

    def __eq__(self, other):
        """Compare iterator heads for equality - as opposed to the entire
        iterators.
        """

        # This is a bit sloppy as it never considers the type of the
        # other element
        return self.lookahead == other.lookahead


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


def fmap(value, funcs):
    """Feeds the same value to a list of functions.

    >>> fmap(-5.5, [str, int, abs])
    ['-5.5', -5, 5.5]
    """

    return [func(value) for func in funcs]


def formatwarning(message, category, filename, lineno):
    """Custom warning formatting."""

    return "%s: %s\n" % (category.__name__, message)


def is_subdir(path1, path2):
    """Returns True if path1 is a subdirectory of path2, otherwise False.

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


def map_dict(func, dict_):
    """Apply func to all items in dict_"""

    for key in dict_.keys():
        dict_[key] = func(dict_[key])
    return dict_


def merge(*iterators):
    """Merge n ordered iterators into one ordered iterator.

    Merge two ordered iterators
    >>> xs = iter(['a1', 'b1', 'c1'])
    >>> ys = iter(['a2', 'b2', 'c2'])
    >>> list(merge(xs, ys))
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
        iterator = Lookahead(iterators[index])
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


def partition(iterable, func):
    """Partition a set of objects into equivalence classes

    Returns a dictionary {func(obj): [equivalent objects]}
    Object o1 and o2 are equivalent if and only if func(o1) == func(o2)

    >>> p = partition(range(0, 10), lambda x: x % 3)

    >>> classes = p.keys()
    >>> classes.sort()
    >>> print classes
    [0, 1, 2]

    >>> print p[0], p[1], p[2]
    [0, 3, 6, 9] [1, 4, 7] [2, 5, 8]
    """

    partitions = {}
    for obj in iterable:
        partitions.setdefault(func(obj), []).append(obj)
    return partitions


def split_dict(dct, pred):
    """Split dictionary in two by a predicate function.

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
        value = locale.format('%d', value)
    elif value < 10:
        value = locale.format('%.2f', value)
    else:
        value = locale.format('%.1f', value)
    return "%s%s" % (value, suffix)


def uniq(list_):
    """make a list with all duplicate elements removed"""

    if not list_:
        return []
    list_[0] = [list_[0]]
    return reduce(lambda A, x: x in A and A or A+[x], list_)
