"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag a"""

    write_dnuos_diff('-q --output=[a] aac case', """
Bitrate(s)
==========

96
96

VBR
VBR
VBR
    """)
