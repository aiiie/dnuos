"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag S"""

    write_dnuos_diff('-q --output=[S] aac', """
Size
====

1622170
1622311
    """)
