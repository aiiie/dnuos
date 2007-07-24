"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff('-q --output=[f] aac', """
Files
=====

1
1
    """)
