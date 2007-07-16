"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff("-qs aac", """
    test1                                           | 1.55M | AAC  | 96 C
    test2                                           | 1.55M | AAC  | 96 C
    """)
