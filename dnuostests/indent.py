"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify custom indentation functionality"""

    write_dnuos_diff("-q --indent=1 aac", """
Album/Artist                                        |  Size | Type | Quality
============================================================================
aac                                                 |       |      | 
 test1                                              | 1.55M | AAC  | 96 C
 test2                                              | 1.55M | AAC  | 96 C
""")
