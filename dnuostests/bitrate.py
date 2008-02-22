"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify minimum MP3 bitrate functionality"""

    write_dnuos_diff("-q --bitrate=320 lame", """
Album/Artist                                        |  Size | Type | Quality
============================================================================
lame                                                |       |      | 
    3903-api                                        |  237k | MP3  | -api
    3961-api                                        |  237k | MP3  | -b 320
    397b1-b320                                      |  237k | MP3  | -b 320
""")
