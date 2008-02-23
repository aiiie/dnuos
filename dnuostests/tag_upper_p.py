"""
>>> test()
"""

import os

from dnuostests.functest import write_dnuos_diff


def test():
    """Verify output tag P"""

    testdata_dir = os.environ['DATA_DIR']
    write_dnuos_diff('-q --output=[P] aac', """
Path
====
%s
%s
%s
    """ % (
    os.path.join(testdata_dir, 'aac'),
    os.path.join(testdata_dir, 'aac', 'test1'),
    os.path.join(testdata_dir, 'aac', 'test2'),
))
