"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff('-q --output=[P] aac', """
Path
====
/home/mspa/share/dnuos/testdata/aac
/home/mspa/share/dnuos/testdata/aac/test1
/home/mspa/share/dnuos/testdata/aac/test2
    """)
