"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    """Verify output tag a"""
    write_dnuos_diff('-q --output=[a] aac', """
Bitrate(s)
==========

96
96
    """)
