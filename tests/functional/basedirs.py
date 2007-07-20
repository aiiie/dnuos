"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff("-q walk walk/inner", """
Album/Artist                                        |  Size | Type | Quality
============================================================================
walk                                                |       |      | 
    b                                               |  146k | MP3  | -apfe
inner                                               |       |      | 
    a                                               |  131k | MP3  | -ape
    """)
