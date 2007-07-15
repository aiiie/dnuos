"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff("-qm merge/*/*", """
Album/Artist                                        |  Size | Type | Quality
============================================================================
a                                                   |  131k | MP3  | -ape
b                                                   |       |      | 
    a                                               |  116k | MP3  | -V 0
    b                                               |  146k | MP3  | -apfe
    b                                               |  117k | MP3  | -V 0 --vbr-new
    c                                               |  125k | MP3  | -apfs
    c                                               | 81.3k | MP3  | -V 4 --vbr-new
    d                                               |  237k | MP3  | -api
c                                                   |  101k | MP3  | -aps
c                                                   |  100k | MP3  | -V 2 --vbr-new
d                                                   |  237k | MP3  | -b 320
""")
