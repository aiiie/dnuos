"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff('-q --output=[n] aac', """
Album/Artist
============
aac
    test1
    test2
    """)
