"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff("-qi case", """
Album/Artist                                        |  Size | Type | Quality
============================================================================
case                                                |       |      | 
    a                                               |  131k | MP3  | -ape
    B                                               |  146k | MP3  | -apfe
    c                                               |  125k | MP3  | -apfs
""")
