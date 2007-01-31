"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff("-q broken", """
Album/Artist                                        |  Size | Type | Quality
============================================================================

Audiotype failed on the following files:
/home/mattias/share/dnuos/testdata/broken/broken.mp3
    """)
