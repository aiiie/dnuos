"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag L"""

    write_dnuos_diff('-q --output=[L] lame/3903-ape', """
Length
======
6
    """)
