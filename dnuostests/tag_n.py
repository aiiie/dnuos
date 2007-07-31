"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag n"""

    write_dnuos_diff('-q --output=[n] aac', """
Album/Artist
============
aac
    test1
    test2
    """)
