"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify VBR-only directory filtering functionality"""

    write_dnuos_diff("-q -v mixed", """
Album/Artist                                        |  Size | Type | Quality
============================================================================
""")
