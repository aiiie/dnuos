"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify wildcard expansion"""

    write_dnuos_diff("-q -w c*", """
Album/Artist                                        |  Size | Type | Quality
============================================================================
case                                                |       |      | 
    B                                               |  146k | MP3  | -apfe
    a                                               |  131k | MP3  | -ape
    c                                               |  125k | MP3  | -apfs
""", no_glob=True)
