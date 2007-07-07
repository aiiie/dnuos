"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    """Verify output tag A"""
    write_dnuos_diff('-q --output=[A] aac', """
Artist
======


jerk
    """)
