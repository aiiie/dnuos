"""
>>> test()
"""

from os import environ

from functest import write_dnuos_diff


def test():
    """Confirm that broken audio files are correctly reported.
    """
    testdata_dir = environ['DATA_DIR']
    write_dnuos_diff("-q broken", """
Album/Artist                                        |  Size | Type | Quality
============================================================================

Audiotype failed on the following files:
%s/broken/broken.mp3
    """ % testdata_dir)
