"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff('-q --output=[S] aac', """
Size
====

1622170
1622311
    """)
