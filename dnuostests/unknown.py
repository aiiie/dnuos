"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify unknown type functionality"""

    write_dnuos_diff("-qs --unknown-types=txt,text unknown", """
unknown                                             |  128  | Mixe | 0 ~
""")
