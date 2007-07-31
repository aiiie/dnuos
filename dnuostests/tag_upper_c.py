"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag C"""

    write_dnuos_diff('-q --output=[C] aac', """
Album
=====


jerk
    """)
