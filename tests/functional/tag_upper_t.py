"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    """Verify output tag T"""

    write_dnuos_diff('-q --output=[T] aac', """
BR Type
=======

C
C
    """)
