"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag N"""

    write_dnuos_diff('-q --output=[N] aac', """
Album/Artist
============
aac
test1
test2
    """)
