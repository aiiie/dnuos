"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify tree merging functionality"""

    write_dnuos_diff("-q merge/*/*", """
Album/Artist                                        |  Size | Type | Quality
============================================================================
a                                                   |  131k | MP3  | -ape
b                                                   |       |      | 
    b                                               |  146k | MP3  | -apfe
    c                                               |  125k | MP3  | -apfs
    d                                               |  237k | MP3  | -api
c                                                   |  101k | MP3  | -aps
b                                                   |       |      | 
    a                                               |  116k | MP3  | -V0
    b                                               |  117k | MP3  | -V0n
    c                                               | 81.3k | MP3  | -V4n
c                                                   |  100k | MP3  | -V2n
d                                                   |  237k | MP3  | -b 320
""")
