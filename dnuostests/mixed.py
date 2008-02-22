"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify mixed directory exclusion functionality"""

    write_dnuos_diff("-q -M mixed", """
Album/Artist                                        |  Size | Type | Quality
============================================================================
""")
