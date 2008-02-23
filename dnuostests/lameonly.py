"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify non-LAME filtering functionality"""

    write_dnuos_diff("-ql nonlame", """
Album/Artist                                        |  Size | Type | Quality
============================================================================
nonlame                                             |       |      | 
    lame                                            | 23.3k | MP3  | -V9n
""")
