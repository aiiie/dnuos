"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff('-q --output=[b] aac', """
Bitrate
=======

96.0k
96.0k
    """)
