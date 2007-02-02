"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff("-qm merge1/* merge2/*", """
Album/Artist                                        |  Size | Type | Quality
============================================================================
alpha                                               |       |      | 
    alpha                                           | 26.9k | MP3  | -V 9
    beta                                            | 23.3k | MP3  | -V 9 --vbr-new
beta                                                |       |      | 
    alpha                                           | 34.1k | MP3  | -V 8 --vbr-new
    alpha                                           | 54.6k | MP3  | -V 6
    beta                                            | 44.4k | MP3  | -V 7
    beta                                            | 51.9k | MP3  | -V 6 --vbr-new
gamma                                               |       |      | 
    alpha                                           | 60.5k | MP3  | -V 5 --vbr-new
    beta                                            | 77.3k | MP3  | -V 4
""")
