"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag q"""

    write_dnuos_diff('-q --output=[q] aac', """
Quality
=======

96 C
96 C
    """)
