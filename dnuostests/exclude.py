"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify directory exclusion functionality"""

    write_dnuos_diff("-q --exclude=aac/test1 aac", """
Album/Artist                                        |  Size | Type | Quality
============================================================================
aac                                                 |       |      | 
    test2                                           | 1.55M | AAC  | 96 C
""")
