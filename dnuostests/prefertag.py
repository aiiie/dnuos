"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify ID3 version preference functionality"""

    write_dnuos_diff("-qs --prefer-tag=2 --output=[A] id3", """
Red
""")
    write_dnuos_diff("-qs --prefer-tag=1 --output=[A] id3", """
Blue
""")
