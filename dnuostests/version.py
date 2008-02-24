"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify version string output"""

    write_dnuos_diff("-V", """
dnuos 1.0b5
""")
