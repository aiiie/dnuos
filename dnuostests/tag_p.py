"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag p"""

    write_dnuos_diff('-q --output=[p] lame/3903-ape', """
Profile
=======
-ape
    """)
