"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag B"""

    write_dnuos_diff('-q --output=[B] aac', """
Bitrate
=======

96000
96000
    """)
