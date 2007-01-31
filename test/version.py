"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff("-V", """
dnuos version:     0.93
audiotype version: 0.94
""")
