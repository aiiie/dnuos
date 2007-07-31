"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verifies basedirs are automatically excluded from ancestor basedirs"""

    write_dnuos_diff("-q walk walk/inner", """
Album/Artist                                        |  Size | Type | Quality
============================================================================
walk                                                |       |      | 
    b                                               |  146k | MP3  | -apfe
inner                                               |       |      | 
    a                                               |  131k | MP3  | -ape
    """)
