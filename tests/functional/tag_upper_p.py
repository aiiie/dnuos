"""
>>> test()
"""

from os import environ

from functest import write_dnuos_diff


def test():
    """Verify output tag P"""
    testdata_dir = environ['DATA_DIR']
    write_dnuos_diff('-q --output=[P] aac', """
Path
====
%s/aac
%s/aac/test1
%s/aac/test2
    """ % ((testdata_dir,)*3))
