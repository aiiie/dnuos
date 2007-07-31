"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag s"""

    write_dnuos_diff('-q --output=[s] aac', """
Size
====

1.55M
1.55M
    """)
