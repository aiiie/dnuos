"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff('-q --output=[q] aac', """
Quality
=======

96 C
96 C
    """)
