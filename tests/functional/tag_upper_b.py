"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff('-q --output=[B] aac', """
Bitrate
=======

96000
96000
    """)
