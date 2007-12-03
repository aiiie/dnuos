"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag l"""

    write_dnuos_diff('-q --output=[V] lame', """
Encoder
=======

LAME3.90.
LAME3.90.
LAME3.90.
LAME3.90.
LAME3.90.
LAME3.96r
LAME3.96r
LAME3.96r
LAME3.96r
LAME3.96r
LAME3.96r
LAME3.96r
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
LAME3.97b
    """)
