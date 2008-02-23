"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify --strip functionality"""

    write_dnuos_diff("-qs --output=[n] aac", """
    test1
    test2
    """)
