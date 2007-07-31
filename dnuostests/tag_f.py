"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag f"""

    write_dnuos_diff('-q --output=[f] aac', """
Files
=====

1
1
    """)
