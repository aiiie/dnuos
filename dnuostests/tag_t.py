"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag t"""

    write_dnuos_diff('-q -q --output=[t] aac', """
Type
====

AAC
AAC
    """)
