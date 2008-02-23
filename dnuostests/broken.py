"""
>>> test()
"""

import os

from dnuostests.functest import write_dnuos_diff


def test():
    """Confirm that broken audio files are correctly reported"""

    testdata_dir = os.environ['DATA_DIR']
    write_dnuos_diff("-q broken", """
Album/Artist                                        |  Size | Type | Quality
============================================================================

Audiotype failed on the following files:
%s
    """ % os.path.join(testdata_dir, 'broken', 'broken.mp3'))
