"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Confirm that bad files are ignored"""

    write_dnuos_diff("-q --ignore-bad broken", """
Album/Artist                                        |  Size | Type | Quality
============================================================================

""")
