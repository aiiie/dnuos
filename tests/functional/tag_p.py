"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff('-q --output=[p] lame/3903-ape', """
Profile
=======
-ape
    """)
