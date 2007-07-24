"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff('-q --output=[L] lame/3903-ape', """
Length
======
6
    """)
