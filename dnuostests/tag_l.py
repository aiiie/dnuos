"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag l"""

    write_dnuos_diff('-q --output=[l] lame/3903-ape', """
Length
======
0:06
    """)
