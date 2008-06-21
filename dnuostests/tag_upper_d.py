"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag q"""

    write_dnuos_diff('-q --output=[D] walk', """
Depth
=====
0
1
1
2
    """)
