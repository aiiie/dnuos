"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    """Verify version string output"""

    write_dnuos_diff("-V", """
dnuos 0.93
""")
