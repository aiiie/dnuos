"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    """Verify output tag m"""

    write_dnuos_diff('-q --output=[m] aac', """
Modified
========

Sat Jul 14 19:39:39 2007
Sat Jul 14 20:39:40 2007
    """)
