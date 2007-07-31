"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag b"""

    write_dnuos_diff('-q --output=[b] aac', """
Bitrate
=======

96.0k
96.0k
    """)
